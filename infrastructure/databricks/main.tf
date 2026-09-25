# infrastructure/databricks/main.tf
# Databricks IaC Configuration (US-14.1)
# Provisions an isolated Databricks workspace ensuring no public IP exposure.

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
  # Skip provider registration for dry-run validation purposes
  skip_provider_registration = true 
}

resource "azurerm_resource_group" "aeris_rg" {
  name     = "aeris-databricks-rg"
  location = "eastus2"
}

resource "azurerm_databricks_workspace" "aeris_compute" {
  name                          = "aeris-databricks-workspace"
  resource_group_name           = azurerm_resource_group.aeris_rg.name
  location                      = azurerm_resource_group.aeris_rg.location
  sku                           = "premium"
  public_network_access_enabled = false

  tags = {
    Environment = "Dev"
    Platform    = "AERIS"
  }
}