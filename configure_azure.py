#!/usr/bin/env python3
"""
Azure OpenAI Auto-Configuration Script
Connects to your Azure account and finds the correct configuration for Nerdbuntu
"""

import sys
import json
import subprocess
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_success(text):
    """Print success message"""
    print(f"✓ {text}")

def print_error(text):
    """Print error message"""
    print(f"✗ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠ {text}")

def check_az_cli():
    """Check if Azure CLI is installed"""
    try:
        result = subprocess.run(['az', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print_success("Azure CLI is installed")
            return True
        else:
            print_error("Azure CLI is installed but not working properly")
            return False
    except FileNotFoundError:
        print_error("Azure CLI is not installed")
        print_info("Install it from: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli")
        return False

def check_login():
    """Check if user is logged into Azure"""
    try:
        result = subprocess.run(['az', 'account', 'show'], capture_output=True, text=True)
        if result.returncode == 0:
            account_info = json.loads(result.stdout)
            print_success(f"Logged in as: {account_info['user']['name']}")
            print_info(f"Subscription: {account_info['name']}")
            return True
        else:
            print_error("Not logged into Azure CLI")
            return False
    except Exception as e:
        print_error(f"Error checking login status: {e}")
        return False

def login_to_azure():
    """Log into Azure"""
    print_info("Opening browser for Azure login...")
    try:
        result = subprocess.run(['az', 'login'], capture_output=True, text=True)
        if result.returncode == 0:
            print_success("Successfully logged into Azure")
            return True
        else:
            print_error("Failed to log into Azure")
            print(result.stderr)
            return False
    except Exception as e:
        print_error(f"Error during login: {e}")
        return False

def find_openai_resources():
    """Find all Azure OpenAI resources in the subscription"""
    print_info("Searching for Azure OpenAI resources...")
    try:
        result = subprocess.run(
            ['az', 'cognitiveservices', 'account', 'list', '--query', 
             "[?kind=='OpenAI']", '-o', 'json'],
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            resources = json.loads(result.stdout)
            if resources:
                print_success(f"Found {len(resources)} Azure OpenAI resource(s)")
                return resources
            else:
                print_warning("No Azure OpenAI resources found in your subscription")
                return []
        else:
            print_error("Failed to list Azure OpenAI resources")
            print(result.stderr)
            return []
    except Exception as e:
        print_error(f"Error finding resources: {e}")
        return []

def get_resource_keys(resource_group, account_name):
    """Get API keys for a resource"""
    try:
        result = subprocess.run(
            ['az', 'cognitiveservices', 'account', 'keys', 'list',
             '--resource-group', resource_group,
             '--name', account_name,
             '-o', 'json'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            keys = json.loads(result.stdout)
            return keys.get('key1')
        else:
            print_warning(f"Could not retrieve keys for {account_name}")
            return None
    except Exception as e:
        print_warning(f"Error getting keys: {e}")
        return None

def get_deployments(resource_group, account_name):
    """Get model deployments for a resource"""
    try:
        result = subprocess.run(
            ['az', 'cognitiveservices', 'account', 'deployment', 'list',
             '--resource-group', resource_group,
             '--name', account_name,
             '-o', 'json'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            deployments = json.loads(result.stdout)
            return deployments
        else:
            return []
    except Exception as e:
        print_warning(f"Error getting deployments: {e}")
        return []

def select_resource(resources):
    """Let user select a resource"""
    if len(resources) == 1:
        print_info(f"Using resource: {resources[0]['name']}")
        return resources[0]
    
    print("\nAvailable Azure OpenAI Resources:")
    for i, resource in enumerate(resources, 1):
        print(f"\n{i}. {resource['name']}")
        print(f"   Location: {resource['location']}")
        print(f"   Resource Group: {resource['resourceGroup']}")
    
    while True:
        try:
            choice = input(f"\nSelect resource (1-{len(resources)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(resources):
                return resources[idx]
            else:
                print_error(f"Please enter a number between 1 and {len(resources)}")
        except ValueError:
            print_error("Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nCancelled by user")
            sys.exit(0)

def select_deployment(deployments):
    """Let user select a deployment"""
    if not deployments:
        print_warning("No deployments found for this resource")
        print_info("You need to create a deployment in Azure Portal first")
        print_info("Visit: https://portal.azure.com → Your OpenAI Resource → Model deployments")
        return None
    
    if len(deployments) == 1:
        print_info(f"Using deployment: {deployments[0]['name']}")
        return deployments[0]
    
    print("\nAvailable Model Deployments:")
    for i, deployment in enumerate(deployments, 1):
        model = deployment.get('properties', {}).get('model', {})
        print(f"\n{i}. {deployment['name']}")
        print(f"   Model: {model.get('name', 'Unknown')}")
        print(f"   Version: {model.get('version', 'Unknown')}")
    
    while True:
        try:
            choice = input(f"\nSelect deployment (1-{len(deployments)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(deployments):
                return deployments[idx]
            else:
                print_error(f"Please enter a number between 1 and {len(deployments)}")
        except ValueError:
            print_error("Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nCancelled by user")
            sys.exit(0)

def save_env_file(endpoint, api_key, deployment_name):
    """Save configuration to .env file"""
    script_dir = Path(__file__).parent
    env_file = script_dir / '.env'
    
    # Check if .env exists
    if env_file.exists():
        response = input("\n.env file already exists. Overwrite? (y/n): ").strip().lower()
        if response != 'y':
            print_info("Cancelled. Not overwriting existing .env file")
            return False
    
    try:
        with open(env_file, 'w') as f:
            f.write("# Azure AI Configuration\n")
            f.write(f"AZURE_ENDPOINT={endpoint}\n")
            f.write(f"AZURE_API_KEY={api_key}\n")
            f.write(f"AZURE_DEPLOYMENT_NAME={deployment_name}\n")
            f.write("\n# Application Settings\n")
            f.write("INPUT_DIR=data/input\n")
            f.write("OUTPUT_DIR=data/output\n")
            f.write("VECTOR_DB_DIR=data/vector_db\n")
            f.write("\n# Processing Settings\n")
            f.write("CHUNK_SIZE=1000\n")
            f.write("MAX_CONCEPTS=10\n")
            f.write("EMBEDDING_MODEL=all-MiniLM-L6-v2\n")
        
        print_success(f"Configuration saved to: {env_file}")
        return True
    except Exception as e:
        print_error(f"Error saving .env file: {e}")
        return False

def main():
    """Main function"""
    print_header("Azure OpenAI Auto-Configuration for Nerdbuntu")
    
    print("This script will:")
    print("  1. Connect to your Azure account")
    print("  2. Find your Azure OpenAI resources")
    print("  3. Discover your model deployments")
    print("  4. Generate the correct .env configuration")
    print()
    
    # Check Azure CLI
    print_header("Step 1: Checking Azure CLI")
    if not check_az_cli():
        print_info("\nPlease install Azure CLI and run this script again")
        sys.exit(1)
    
    # Check login status
    print_header("Step 2: Checking Azure Login")
    if not check_login():
        print_info("You need to log into Azure")
        if not login_to_azure():
            sys.exit(1)
    
    # Find OpenAI resources
    print_header("Step 3: Finding Azure OpenAI Resources")
    resources = find_openai_resources()
    
    if not resources:
        print_error("\nNo Azure OpenAI resources found!")
        print_info("Please create an Azure OpenAI resource first:")
        print_info("  1. Go to https://portal.azure.com")
        print_info("  2. Create a new Azure OpenAI resource")
        print_info("  3. Run this script again")
        sys.exit(1)
    
    # Select resource
    print_header("Step 4: Selecting Resource")
    selected_resource = select_resource(resources)
    
    resource_name = selected_resource['name']
    resource_group = selected_resource['resourceGroup']
    location = selected_resource['location']
    
    # Build endpoint URL
    endpoint = f"https://{resource_name}.openai.azure.com/"
    print_success(f"Endpoint: {endpoint}")
    
    # Get API key
    print_header("Step 5: Retrieving API Key")
    api_key = get_resource_keys(resource_group, resource_name)
    
    if not api_key:
        print_error("Could not retrieve API key")
        print_info("You may need to retrieve it manually from Azure Portal")
        sys.exit(1)
    
    print_success("API key retrieved successfully")
    print_info(f"Key: {api_key[:8]}...{api_key[-4:]}")
    
    # Get deployments
    print_header("Step 6: Finding Model Deployments")
    deployments = get_deployments(resource_group, resource_name)
    
    if not deployments:
        print_warning("\nNo model deployments found!")
        print_info("You need to create a deployment first:")
        print_info("  1. Go to https://portal.azure.com")
        print_info(f"  2. Navigate to your resource: {resource_name}")
        print_info("  3. Go to 'Model deployments'")
        print_info("  4. Create a new deployment (e.g., gpt-4 or gpt-35-turbo)")
        print_info("  5. Run this script again")
        sys.exit(1)
    
    # Select deployment
    print_header("Step 7: Selecting Deployment")
    selected_deployment = select_deployment(deployments)
    
    if not selected_deployment:
        sys.exit(1)
    
    deployment_name = selected_deployment['name']
    print_success(f"Selected deployment: {deployment_name}")
    
    # Save configuration
    print_header("Step 8: Saving Configuration")
    print("\nConfiguration Summary:")
    print(f"  Endpoint:    {endpoint}")
    print(f"  API Key:     {api_key[:8]}...{api_key[-4:]}")
    print(f"  Deployment:  {deployment_name}")
    print()
    
    if save_env_file(endpoint, api_key, deployment_name):
        print_header("✓ Configuration Complete!")
        print("\nYour Azure OpenAI is now configured for Nerdbuntu!")
        print("\nNext steps:")
        print("  1. Launch the GUI: ./launch_gui.sh")
        print("  2. Enable semantic features in the GUI options")
        print("  3. Start converting PDFs with AI-powered analysis!")
        print()
    else:
        print_error("Failed to save configuration")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
