import hail as hl
import pandas as pd
import requests
import json
import os

def get_gene_coordinates(ensembl_id):
    """Fetch gene coordinates from Ensembl REST API."""
    server = "https://rest.ensembl.org"
    endpoint = f"/lookup/id/{ensembl_id}?expand=1"
    
    try:
        response = requests.get(server + endpoint, headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            data = response.json()
            return {
                'chrom': str(data['seq_region_name']),
                'start': data['start'],
                'end': data['end'],
                'gene_name': data.get('display_name', ensembl_id)
            }
        else:
            print(f"Failed to fetch coordinates for {ensembl_id}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching coordinates for {ensembl_id}: {e}")
        return None

def download_gnomad_chd_data(ensembl_ids, output_file='chd1_9_variants.csv'):
    """Download gnomAD data for multiple genes and save to CSV."""
    # Initialize Hail
    hl.init()

    # Load gnomAD v3.1 genomes dataset
    gnomad_dataset = 'gs://gnomad-public-legacy/release/3.1.2/ht/genomes/gnomad.genomes.v3.1.2.hg38.ht'
    mt = hl.read_matrix_table(gnomad_dataset)

    # List to store DataFrames
    all_dfs = []

    # Process each gene
    for ensembl_id in ensembl_ids:
        # Get gene coordinates
        gene_info = get_gene_coordinates(ensembl_id)
        if not gene_info:
            print(f"Skipping {ensembl_id} due to missing coordinates")
            continue

        chrom = gene_info['chrom']
        start = gene_info['start']
        end = gene_info['end']
        gene_name = gene_info['gene_name']
        print(f"Processing {gene_name} ({ensembl_id}) on chr{chrom}:{start}-{end}")

        # Filter variants to the gene's genomic region
        mt_gene = mt.filter_rows(
            (mt.locus.contig == chrom) &
            (mt.locus.position >= start) &
            (mt.locus.position <= end)
        )

        # Select relevant fields
        mt_gene = mt_gene.select_rows(
            variant_id=mt_gene.rsid,
            chrom=mt_gene.locus.contig,
            pos=mt_gene.locus.position,
            ref=mt_gene.alleles[0],
            alt=mt_gene.alleles[1],
            af=mt_gene.freq[0].AF,  # Allele frequency
            an=mt_gene.freq[0].AN,  # Allele number
            ac=mt_gene.freq[0].AC,  # Allele count
            gene=hl.literal(gene_name)  # Add gene name as a column
        )

        # Convert to Hail Table and then to Pandas DataFrame
        table = mt_gene.rows()
        df = table.to_pandas()
        
        if not df.empty:
            all_dfs.append(df)
        else:
            print(f"No variants found for {gene_name}")

    # Combine all DataFrames
    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
        # Save to CSV
        final_df.to_csv(output_file, index=False)
        print(f"Data saved to {output_file} with {len(final_df)} variants")
    else:
        print("No data to save")

    # Stop Hail
    hl.stop()

if __name__ == '__main__':
    # Ensembl IDs for CHD1 to CHD9
    chd_genes = [
        'ENSG00000153922',  # CHD1
        'ENSG00000173575',  # CHD2
        'ENSG00000170004',  # CHD3
        'ENSG00000111642',  # CHD4
        'ENSG00000116254',  # CHD5
        'ENSG00000124177',  # CHD6
        'ENSG00000171346',  # CHD7
        'ENSG00000100888',  # CHD8
        'ENSG00000177200'   # CHD9
    ]
    
    # Download data
    download_gnomad_chd_data(chd_genes, 'chd1_9_variants.csv')
    