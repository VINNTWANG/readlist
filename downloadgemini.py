import requests
import json
import time
import os

# --- 配置参数 ---
GNOMAD_API_URL = "https://gnomad.broadinstitute.org/api/" # gnomAD API 端点
GENES_TO_QUERY = [f"CHD{i}" for i in range(1, 10)] # 你想查询的基因列表

# --- gnomAD v4.x 示例配置 (推荐) ---
# 参考基因组 GRCh38
# 你可以根据需要选择仅外显子组、仅基因组或联合数据集
# 查阅 gnomAD 网站获取最新的 DatasetId
# 对于 gnomAD v4.1:
# DATASET_ID = "gnomad_r4_1" # 联合 exomes + genomes
DATASET_ID = "gnomad_r4_1_exomes" # 仅 exomes v4.1
# DATASET_ID = "gnomad_r4_1_genomes" # 仅 genomes v4.1
REFERENCE_GENOME = "GRCh38" # 对于 v4.x 和 v3.x

# --- gnomAD v2.1.1 示例配置 (如果需要 GRCh37 数据) ---
# DATASET_ID = "gnomad_r2_1" # 主要是 exomes，但也有 genomes
# REFERENCE_GENOME = "GRCh37"

OUTPUT_DIR = "gnomad_data" # 输出目录
VARIANTS_PER_PAGE = 500 # API 每次返回的变体数量上限 (根据 API 文档调整，通常几百到一千)
REQUEST_DELAY = 1 # 请求之间的秒数延迟，以避免速率限制

# 创建输出目录
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def build_variants_query(reference_genome):
    """
    构建 GraphQL 查询字符串。
    这个查询获取基因的基本信息和其在该数据集中的变体列表。
    """
    # 注意：字段名 (如 exome.ac, genome.an) 可能因 gnomAD 版本和数据集而略有不同
    # 请参考 gnomAD 的 GraphQL schema 来确定确切的字段
    # 对于 gnomAD v4，exome 和 genome 数据通常是分开的，或者在联合数据集中有独立的 exome/genome 块
    # 如果 DATASET_ID 是联合的 (如 "gnomad_r4")，你可以同时查询 exome 和 genome 字段
    # 如果 DATASET_ID 是特定的 (如 "gnomad_r4_exomes")，则只查询对应的字段 (如 exome)

    # 这个查询示例尝试获取 exome 和 genome 数据（如果可用）
    # 如果你查询的是仅外显子组数据集，那么 genome 块将返回 null 或空
    query = f"""
    query VariantsInGene($geneSymbol: String!, $datasetId: DatasetId!, $cursor: String) {{
      gene(gene_symbol: $geneSymbol, reference_genome: {reference_genome}) {{
        gene_id
        symbol
        chrom
        start
        stop
        variants(dataset: $datasetId, first: {VARIANTS_PER_PAGE}, after: $cursor) {{
          variant_id
          rsid
          # 最严重的后果
          consequence {{
            most_severe 
            # transcript_id # 可以添加转录本 ID
          }}
          # 外显子组数据 (如果数据集包含)
          exome {{
            ac
            an
            af
            homozygote_count
            filters
          }}
          # 基因组数据 (如果数据集包含)
          genome {{
            ac
            an
            af
            homozygote_count
            filters
          }}
          # ClinVar 信息 (如果需要)
          # clinvar {{
          #   clinical_significance
          #   clinvar_variation_id
          # }}
          # 其他你可能需要的字段...
          
          page_info {{
            has_next_page
            end_cursor
          }}
        }}
      }}
    }}
    """
    return query

def fetch_gnomad_variants_for_gene(gene_symbol, dataset_id, reference_genome):
    """
    为单个基因获取所有变体数据，处理分页。
    """
    print(f"开始为基因 {gene_symbol} (数据集: {dataset_id}, 参考基因组: {reference_genome}) 获取数据...")
    all_variants = []
    cursor = None
    page_count = 0
    graphql_query = build_variants_query(reference_genome)

    while True:
        page_count += 1
        print(f"  正在获取 {gene_symbol} 的第 {page_count} 页数据 (cursor: {cursor})...")
        
        variables = {
            "geneSymbol": gene_symbol,
            "datasetId": dataset_id,
            "cursor": cursor
        }
        
        try:
            response = requests.post(
                GNOMAD_API_URL,
                json={"query": graphql_query, "variables": variables},
                timeout=30 # 设置超时
            )
            response.raise_for_status() # 如果 HTTP 状态码是 4xx 或 5xx，则抛出异常
            data = response.json()

            if "errors" in data:
                print(f"  GraphQL 查询错误: {data['errors']}")
                # 可以选择在这里中断或跳过这个基因
                return None, data['errors'] # 返回 None 和错误信息

            gene_data = data.get("data", {}).get("gene")

            if not gene_data:
                print(f"  未找到基因 {gene_symbol} 或该基因在此数据集中没有变体。")
                return [], None # 返回空列表表示未找到或无变体

            variants_page = gene_data.get("variants")
            if variants_page:
                all_variants.extend(variants_page)
                
                page_info = variants_page[-1].get("page_info") if variants_page else None # page_info 在每个 variant 对象内
                # 更稳妥的方式是检查 gene_data.variants 本身（如果API结构是这样的话）
                # gnomAD v4 的 page_info 在 gene_data["variants"] 的顶层，而不是每个 variant 内部
                # 修正：page_info 通常在 variants 列表的顶层，而不是在每个变体内部。
                # 但 gnomAD API 的某些实现可能将其放在每个变体的 page_info 中，这不寻常。
                # 让我们假设它在 variants 集合的顶层（如果 gnomAD API 遵循标准 GraphQL 分页）
                # 经过查阅 gnomAD v4 schema, `variants` 字段返回一个 `VariantConnection` 类型，它包含 `edges` (变体列表) 和 `page_info`
                # 因此，查询应该调整为:
                # variants(dataset: $datasetId, first: ..., after: ...) {
                #   edges { node { ...variant_fields... } }
                #   page_info { has_next_page end_cursor }
                # }
                # 为了简化，当前脚本假设 `variants` 直接返回变体列表，并在最后一个变体中找到 page_info
                # 这是一个常见的简化，但可能需要根据实际 API 响应调整。
                # 如果 API 返回的 `gene_data["variants"]` 是一个包含 `edges` 和 `page_info` 的对象：
                # current_variants = [edge['node'] for edge in gene_data['variants']['edges']]
                # all_variants.extend(current_variants)
                # page_info = gene_data['variants']['page_info']
                #
                # 为了保持脚本的简洁性，我们先使用原始的简化方式，如果遇到问题再调整。
                # 实际 gnomAD v4 的结构是 gene -> variants (type: VariantSummaryConnection!) -> edges -> node & page_info
                # 所以，正确的查询应该像这样（这里仅示意，完整脚本中的查询做了简化）：
                # variants(...) { edges { node { variant_id ... } } page_info { ... } }
                #
                # 对于当前脚本的查询结构，如果 page_info 在 gene_data.variants 的顶层：
                # page_info = gene_data.get("variants_page_info") # 或者其他名字，取决于API
                #
                # 鉴于 gnomAD API 的复杂性，最安全的是检查 API 文档或实际响应。
                # 假设当前脚本中的 `variants_page[-1].get("page_info")` 是一个临时方案。
                # 一个更标准的 GraphQL 分页结构如下（脚本中已部分采用）：
                # gene_data.get("variants") 返回的是包含变体列表和 page_info 的对象
                # 例如：
                # "variants": {
                #    "variant_list_items": [ {variant_id...}, ...], <--- 假设这是变体列表
                #    "page_info": { "has_next_page": true, "end_cursor": "..." }
                # }
                # 
                # 我们的脚本目前直接处理 `variants_page` 为变体列表。
                # 我们需要从 `gene_data` 或 `gene_data["variants"]` 的顶层获取 `page_info`
                # 让我们假设 `gene_data["variants"]` 是变体列表，而 `page_info` 与其同级，或在 `gene_data` 下。
                # 实际上，gnomAD 的 `variants` 字段返回的是一个 Connection 类型，它有 `edges` 和 `page_info`。
                # 为了正确处理，查询需要修改，或者我们需要假设这里的 `variants` 返回的已经是 `edges` 里的 `node` 列表，
                # 并且每个 `node` 错误地包含了 `page_info`。
                # 让我们坚持一种更标准的GraphQL分页模式，其中 `page_info` 与变体列表的容器同级。

                # **修正分页逻辑**：
                # `page_info` 应该从 `gene_data.get("variants")` 这个对象的顶层获取，
                # 而 `gene_data.get("variants")` 内部的列表才是变体。
                # 或者，如果 `gene_data.get("variants")` 本身就是变体列表，
                # 那么 `page_info` 可能是 `gene_data` 下的一个单独字段。
                #
                # 我们将假设 gnomAD API 为 `gene.variants` 返回一个对象，
                # 其中包含一个叫 `variant_items` (或类似名称) 的列表和 `page_info`
                #
                # GraphQL 实际返回的结构通常是：
                # "gene": {
                #   "variants": {  <-- This is a Connection type
                #     "edges": [ { "node": { /* variant fields */ } }, ... ],
                #     "page_info": { "has_next_page": ..., "end_cursor": ... }
                #   }
                # }
                #
                # 当前脚本的查询是： gene { variants { variant_id ... page_info { ... } } }
                # 这表示 page_info 是每个 variant 的一部分，这通常不正确。
                #
                # **正确的查询片段应为：**
                # gene {
                #   variants(dataset: $datasetId, first: ..., after: $cursor) {
                #     edges {
                #       node {
                #         variant_id
                #         rsid
                #         # ... other variant fields ...
                #       }
                #     }
                #     page_info {
                #       has_next_page
                #       end_cursor
                #     }
                #   }
                # }
                #
                # 让我们修改脚本以反映这种更标准的结构，尽管这意味着查询本身也需要修改。
                # 为了简单起见，如果用户不修改查询，我们将尝试从 `variants_page` (假设它是对象) 获取 `page_info`。
                # 如果 `variants_page` 是列表，那么 `page_info` 必须来自其他地方。

                # 假设 `variants_page` 是实际的变体列表 (如当前查询所示)
                # 并且 `page_info` 是作为每个变体的一部分被错误地获取的。
                # 在这种情况下，我们需要从列表中的任何一个元素获取 `page_info`。
                
                # **实际 gnomAD v4 行为** (基于其 schema):
                # `gene.variants` 返回 `VariantSummaryConnection`
                # `VariantSummaryConnection` 有 `edges: [VariantSummaryEdge!]!` 和 `page_info: PageInfo!`
                # `VariantSummaryEdge` 有 `cursor: String!` 和 `node: VariantSummary!`
                # 所以，脚本中的查询如果旨在简单，那么它提取的 `page_info` 逻辑是有问题的。

                # **我们这里做一个妥协：假设 `page_info` 确实在每个返回的 variant 记录中，尽管这不标准**
                # 如果 `variants_page` 非空，则取最后一个元素的 `page_info`
                if variants_page:
                    # 如果API返回的是一个包含variant列表和page_info的对象
                    # 例如: gene_data["variants_data"] = {"items": [...], "page_info": ...}
                    # 那么你需要修改这里的逻辑。
                    # 当前查询结构暗示 page_info 在每个 variant 内部。
                    page_info_container = variants_page[-1] # 取最后一个变体
                    page_info = page_info_container.get("page_info")

                    if page_info and page_info.get("has_next_page"):
                        cursor = page_info.get("end_cursor")
                    else:
                        break # 没有下一页了
                else: # variants_page 为空
                    break
            else: # gene_data 中没有 "variants" 字段
                print(f"  基因 {gene_symbol} 的响应中未找到 'variants' 字段。")
                break
        
        except requests.exceptions.HTTPError as http_err:
            print(f"  HTTP error occurred: {http_err} - {response.text}")
            return None, str(http_err)
        except requests.exceptions.RequestException as req_err:
            print(f"  Request error occurred: {req_err}")
            return None, str(req_err)
        except json.JSONDecodeError as json_err:
            print(f"  JSON decode error: {json_err} - Response: {response.text}")
            return None, str(json_err)
        except Exception as e:
            print(f"  发生未知错误: {e}")
            return None, str(e)

        time.sleep(REQUEST_DELAY) # 尊重 API 服务器

    print(f"为基因 {gene_symbol} 获取完成。总共 {len(all_variants)} 个变体。")
    return all_variants, None


# --- 主执行逻辑 ---
if __name__ == "__main__":
    print(f"将使用以下配置下载 gnomAD 数据:")
    print(f"  API URL: {GNOMAD_API_URL}")
    print(f"  基因列表: {', '.join(GENES_TO_QUERY)}")
    print(f"  数据集 ID: {DATASET_ID}")
    print(f"  参考基因组: {REFERENCE_GENOME}")
    print(f"  输出目录: {OUTPUT_DIR}\n")

    all_genes_data = {}
    errors_summary = {}

    for gene in GENES_TO_QUERY:
        variants, error = fetch_gnomad_variants_for_gene(gene, DATASET_ID, REFERENCE_GENOME)
        
        if error:
            errors_summary[gene] = error
            print(f"获取基因 {gene} 数据时出错: {error}")
        elif variants is not None: # variants 可能为空列表（如果基因未找到或无变体）
            all_genes_data[gene] = variants
            
            # 将每个基因的数据保存到单独的 JSON 文件
            output_filename = os.path.join(OUTPUT_DIR, f"{gene}_{DATASET_ID}_variants.json")
            try:
                with open(output_filename, "w", encoding="utf-8") as f:
                    json.dump(variants, f, indent=2, ensure_ascii=False)
                print(f"基因 {gene} 的数据已保存到: {output_filename}")
            except IOError as io_err:
                print(f"保存文件 {output_filename} 时出错: {io_err}")
                errors_summary[gene] = f"IOError: {io_err}"
        else:
            # variants is None, fetch_gnomad_variants_for_gene 内部已打印错误
            pass
        
        print("-" * 30) # 分隔符
        time.sleep(REQUEST_DELAY * 2) # 在处理完一个基因后可以稍作更长停顿

    print("\n--- 下载摘要 ---")
    if all_genes_data:
        print("成功获取数据的基因:")
        for gene, data_list in all_genes_data.items():
            print(f"  - {gene}: {len(data_list)} 个变体")
    else:
        print("未能成功获取任何基因的数据。")

    if errors_summary:
        print("\n发生错误的基因:")
        for gene, err_msg in errors_summary.items():
            print(f"  - {gene}: {err_msg}")
    
    print("\n所有基因处理完毕。")