#!/bin/bash

# Define bash variables; this script is sourced by the other scripts.
# Chris Joakim, 2025

export subscription=$AZURE_SUBSCRIPTION_ID
export user=$USER
export primary_region="eastus"
export primary_rg="cjoakim-ai-research2"

export ai_search_name="cjoakimaisearch"
export ai_search_rg=$primary_rg

export storage_region=$primary_region
export storage_rg=$primary_rg
export storage_name="cjoakimaistorage"
export storage_kind="BlobStorage"     # {BlobStorage, BlockBlobStorage, FileStorage, Storage, StorageV2}]
export storage_sku="Standard_LRS"     # {Premium_LRS, Premium_ZRS, Standard_GRS, Standard_GZRS, , Standard_RAGRS, Standard_RAGZRS, Standard_ZRS]
export storage_access_tier="Hot"      # Cool, Hot

export storage_adlsgen2_region=$primary_region
export storage_adlsgen2_rg=$primary_rg
export storage_adlsgen2_name="cjoakimaiadlsstorage"
export storage_adlsgen2_kind="BlobStorage"     # {BlobStorage, BlockBlobStorage, FileStorage, Storage, StorageV2}]
export storage_adlsgen2_sku="Standard_LRS"     # {Premium_LRS, Premium_ZRS, Standard_GRS, Standard_GZRS, , Standard_RAGRS, Standard_RAGZRS, Standard_ZRS]
export storage_adlsgen2_access_tier="Hot"      # Cool, Hot

export cosmos_nosql_region=$primary_region
export cosmos_nosql_rg=$primary_rg
export cosmos_nosql_acct_name="cjoakimaicosmos"
export cosmos_nosql_dbname="dev"
export cosmos_nosql_cname="pythonlibs"
export cosmos_nosql_pk="/pk"

export log_analytics_region=$primary_region
export log_analytics_rg=$primary_rg
export log_analytics_name="cjoakimailoganalytics"

export app_insights_region=$primary_region
export app_insights_rg=$primary_rg
export app_insights_name="cjoakimaiappinsights"

export kv_name="cjoakimaikeyvault2"
export kv_rg=$primary_rg

export cogsvcs_region=$primary_region
export cogsvcs_rg=$primary_rg
export cogsvcs_name="cjoakimailoganalytics"

export aoai_name="cjoakimaiaoai"
export aoai_rg=$primary_rg
export aoai_region=$primary_region

export foundry_name="cjoakimaifoundry2"
export foundry_rg=$primary_rg
export foundry_region=$primary_region

export docintel_name="cjoakimdocintel"
export docintel_rg=$primary_rg
export docintel_region=$primary_region
