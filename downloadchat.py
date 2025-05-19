import requests
import pandas as pd
import time

# 1. gnomAD GraphQL 端点
gnomad_api = "https://gnomad.broadinstitute.org/api"

# 2. 上面获得的基因坐标
# gene_coords = {...}

# 3. GraphQL 查询模板
query = """
query ($chrom: String!, $start: Int!, $stop: Int!) {
  region(chrom: $chrom, start: $start, stop: $stop) {
    variants {
      variantId
      pos
      ref
      alt
      genomeAnnotations {
        consequence
      }
      alleleFreq {
        global {
          allele_freq
          homozygote_count
          hemizygote_count
        }
      }
    }
  }
}
"""

all_variants = []

for gene, coords in gene_coords.items():
    variables = {
        "chrom": coords["chrom"],
        "start": coords["start"],
        "stop": coords["end"]
    }
    resp = requests.post(
        gnomad_api,
        json={"query": query, "variables": variables}
    )
    result = resp.json()
    for v in result["data"]["region"]["variants"]:
        v["gene"] = gene
        all_variants.append(v)
    # 为防限流，稍作停顿
    time.sleep(1)

# 4. 保存为 CSV
df = pd.json_normalize(all_variants)
df.to_csv("CHD1-9_gnomad_variants.csv", index=False)
print("已保存至 CHD1-9_gnomad_variants.csv")
