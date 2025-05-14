from mcp.server.fastmcp import FastMCP
from netbox_client import NetBoxRestClient
import os
from dotenv import load_dotenv
# Load environment variables from a .env file
load_dotenv()

import logging
logging.basicConfig(level=logging.INFO)

# Mapping of simple object names to API endpoints

NETBOX_OBJECT_TYPES = {
    # DCIM (Device and Infrastructure)
    "cables": "dcim/cables",
    "console-ports": "dcim/console-ports", 
    "console-server-ports": "dcim/console-server-ports",
    "devices": "dcim/devices",
    "device-bays": "dcim/device-bays",
    "device-roles": "dcim/device-roles",
    "device-types": "dcim/device-types",
    "front-ports": "dcim/front-ports",
    "interfaces": "dcim/interfaces",
    "inventory-items": "dcim/inventory-items",
    "locations": "dcim/locations",
    "manufacturers": "dcim/manufacturers",
    "modules": "dcim/modules",
    "module-bays": "dcim/module-bays",
    "module-types": "dcim/module-types",
    "platforms": "dcim/platforms",
    "power-feeds": "dcim/power-feeds",
    "power-outlets": "dcim/power-outlets",
    "power-panels": "dcim/power-panels",
    "power-ports": "dcim/power-ports",
    "racks": "dcim/racks",
    "rack-reservations": "dcim/rack-reservations",
    "rack-roles": "dcim/rack-roles",
    "regions": "dcim/regions",
    "sites": "dcim/sites",
    "site-groups": "dcim/site-groups",
    "virtual-chassis": "dcim/virtual-chassis",
    
    # IPAM (IP Address Management)
    "asns": "ipam/asns",
    "asn-ranges": "ipam/asn-ranges", 
    "aggregates": "ipam/aggregates",
    "fhrp-groups": "ipam/fhrp-groups",
    "ip-addresses": "ipam/ip-addresses",
    "ip-ranges": "ipam/ip-ranges",
    "prefixes": "ipam/prefixes",
    "rirs": "ipam/rirs",
    "roles": "ipam/roles",
    "route-targets": "ipam/route-targets",
    "services": "ipam/services",
    "vlans": "ipam/vlans",
    "vlan-groups": "ipam/vlan-groups",
    "vrfs": "ipam/vrfs",
    
    # Circuits
    "circuits": "circuits/circuits",
    "circuit-types": "circuits/circuit-types",
    "circuit-terminations": "circuits/circuit-terminations",
    "providers": "circuits/providers",
    "provider-networks": "circuits/provider-networks",
    
    # Virtualization
    "clusters": "virtualization/clusters",
    "cluster-groups": "virtualization/cluster-groups",
    "cluster-types": "virtualization/cluster-types",
    "virtual-machines": "virtualization/virtual-machines",
    "vm-interfaces": "virtualization/interfaces",
    
    # Tenancy
    "tenants": "tenancy/tenants",
    "tenant-groups": "tenancy/tenant-groups",
    "contacts": "tenancy/contacts",
    "contact-groups": "tenancy/contact-groups",
    "contact-roles": "tenancy/contact-roles",
    
    # VPN
    "ike-policies": "vpn/ike-policies",
    "ike-proposals": "vpn/ike-proposals",
    "ipsec-policies": "vpn/ipsec-policies",
    "ipsec-profiles": "vpn/ipsec-profiles",
    "ipsec-proposals": "vpn/ipsec-proposals",
    "l2vpns": "vpn/l2vpns",
    "tunnels": "vpn/tunnels",
    "tunnel-groups": "vpn/tunnel-groups",
    
    # Wireless
    "wireless-lans": "wireless/wireless-lans",
    "wireless-lan-groups": "wireless/wireless-lan-groups",
    "wireless-links": "wireless/wireless-links"
}

mcp = FastMCP("NetBox", log_level="DEBUG")
netbox = None

@mcp.tool(name="get_objects", description="Get objects from NetBox based on their type and filters")
def get_objects(object_type: str, filters: dict):
    """
    Get objects from NetBox based on their type and filters
    Args:
        object_type: String representing the NetBox object type (e.g. "devices", "ip-addresses")
        filters: dict of filters to apply to the API call based on the NetBox API filtering options
    
    Valid object_type values:
    
    DCIM (Device and Infrastructure):
    - cables
    - console-ports
    - console-server-ports  
    - devices
    - device-bays
    - device-roles
    - device-types
    - front-ports
    - interfaces
    - inventory-items
    - locations
    - manufacturers
    - modules
    - module-bays
    - module-types
    - platforms
    - power-feeds
    - power-outlets
    - power-panels
    - power-ports
    - racks
    - rack-reservations
    - rack-roles
    - regions
    - sites
    - site-groups
    - virtual-chassis
    
    IPAM (IP Address Management):
    - asns
    - asn-ranges
    - aggregates 
    - fhrp-groups
    - ip-addresses
    - ip-ranges
    - prefixes
    - rirs
    - roles
    - route-targets
    - services
    - vlans
    - vlan-groups
    - vrfs
    
    Circuits:
    - circuits
    - circuit-types
    - circuit-terminations
    - providers
    - provider-networks
    
    Virtualization:
    - clusters
    - cluster-groups
    - cluster-types
    - virtual-machines
    - vm-interfaces
    
    Tenancy:
    - tenants
    - tenant-groups
    - contacts
    - contact-groups
    - contact-roles
    
    VPN:
    - ike-policies
    - ike-proposals
    - ipsec-policies
    - ipsec-profiles
    - ipsec-proposals
    - l2vpns
    - tunnels
    - tunnel-groups
    
    Wireless:
    - wireless-lans
    - wireless-lan-groups
    - wireless-links
    
    See NetBox API documentation for filtering options for each object type.
    """
    # Validate object_type exists in mapping
    if object_type not in NETBOX_OBJECT_TYPES:
        valid_types = "\n".join(f"- {t}" for t in sorted(NETBOX_OBJECT_TYPES.keys()))
        raise ValueError(f"Invalid object_type. Must be one of:\n{valid_types}")
        
    # Get API endpoint from mapping
    endpoint = NETBOX_OBJECT_TYPES[object_type]

    logging.info(f"Fetching objects from endpoint: {endpoint} with filters: {filters}")
    # Make API call
    return netbox.get(endpoint, params=filters)


@mcp.tool(name="get_object_by_id", description="Get detailed information about a specific NetBox object by its ID")
def get_object_by_id(object_type: str, object_id: int):
    """
    Get detailed information about a specific NetBox object by its ID.
    
    Args:
        object_type: String representing the NetBox object type (e.g. "devices", "ip-addresses")
        object_id: The numeric ID of the object
    
    Returns:
        Complete object details
    """
    # Validate object_type exists in mapping
    if object_type not in NETBOX_OBJECT_TYPES:
        valid_types = "\n".join(f"- {t}" for t in sorted(NETBOX_OBJECT_TYPES.keys()))
        raise ValueError(f"Invalid object_type. Must be one of:\n{valid_types}")
        
    # Get API endpoint from mapping
    endpoint = f"{NETBOX_OBJECT_TYPES[object_type]}/{object_id}"
    
    return netbox.get(endpoint)

@mcp.tool(name="get_changelogs", description="Get object change records (changelogs) from NetBox")
def get_changelogs(filters: dict):
    """
    Get object change records (changelogs) from NetBox based on filters.
    
    Args:
        filters: dict of filters to apply to the API call based on the NetBox API filtering options
    
    Returns:
        List of changelog objects matching the specified filters
    
    Filtering options include:
    - user_id: Filter by user ID who made the change
    - user: Filter by username who made the change
    - changed_object_type_id: Filter by ContentType ID of the changed object
    - changed_object_id: Filter by ID of the changed object
    - object_repr: Filter by object representation (usually contains object name)
    - action: Filter by action type (created, updated, deleted)
    - time_before: Filter for changes made before a given time (ISO 8601 format)
    - time_after: Filter for changes made after a given time (ISO 8601 format)
    - q: Search term to filter by object representation

    Example:
    To find all changes made to a specific device with ID 123:
    {"changed_object_type_id": "dcim.device", "changed_object_id": 123}
    
    To find all deletions in the last 24 hours:
    {"action": "delete", "time_after": "2023-01-01T00:00:00Z"}
    
    Each changelog entry contains:
    - id: The unique identifier of the changelog entry
    - user: The user who made the change
    - user_name: The username of the user who made the change
    - request_id: The unique identifier of the request that made the change
    - action: The type of action performed (created, updated, deleted)
    - changed_object_type: The type of object that was changed
    - changed_object_id: The ID of the object that was changed
    - object_repr: String representation of the changed object
    - object_data: The object's data after the change (null for deletions)
    - object_data_v2: Enhanced data representation
    - prechange_data: The object's data before the change (null for creations)
    - postchange_data: The object's data after the change (null for deletions)
    - time: The timestamp when the change was made
    """
    endpoint = "core/object-changes"
    
    # Make API call
    return netbox.get(endpoint, params=filters)

@mcp.tool(name="create_object", description="Create a new object in NetBox")
def create_object(object_type: str, data: dict):
    """
    Create a new object in NetBox.
    
    Args:
        object_type: String representing the NetBox object type (e.g. "devices", "ip-addresses")
        data: Dictionary containing the data for the new object
    
    Returns:
        The created object with its ID and other details
    
    Example:
    To create a new device:
    {
        "name": "router1",
        "device_type": 1,
        "device_role": 1,
        "site": 1,
        "status": "active"
    }
    
    See NetBox API documentation for required and optional fields for each object type.
    """
    # Validate object_type exists in mapping
    if object_type not in NETBOX_OBJECT_TYPES:
        valid_types = "\n".join(f"- {t}" for t in sorted(NETBOX_OBJECT_TYPES.keys()))
        raise ValueError(f"Invalid object_type. Must be one of:\n{valid_types}")
        
    # Get API endpoint from mapping
    endpoint = NETBOX_OBJECT_TYPES[object_type]
    
    # Make API call to create object
    return netbox.create(endpoint, data=data)

@mcp.tool(name="update_object", description="Update an existing object in NetBox")
def update_object(object_type: str, object_id: int, data: dict):
    """
    Update an existing object in NetBox using PATCH method.
    
    Args:
        object_type: String representing the NetBox object type (e.g. "devices", "ip-addresses")
        object_id: The numeric ID of the object to update
        data: Dictionary containing the fields to update
    
    Returns:
        The updated object with its modified fields
    
    Example:
    To update a device with ID 123:
    {
        "name": "new-router-name",
        "status": "maintenance"
    }
    
    Note: Only include the fields you want to update in the data dictionary.
    """
    # Validate object_type exists in mapping
    if object_type not in NETBOX_OBJECT_TYPES:
        valid_types = "\n".join(f"- {t}" for t in sorted(NETBOX_OBJECT_TYPES.keys()))
        raise ValueError(f"Invalid object_type. Must be one of:\n{valid_types}")
        
    # Get API endpoint from mapping
    endpoint = f"{NETBOX_OBJECT_TYPES[object_type]}"
    
    # Make API call to update object using PATCH method
    return netbox.update(endpoint,id=object_id, data=data)

@mcp.tool(name="delete_object", description="Delete an object from NetBox by its ID")
def delete_object(object_type: str, object_id: int):
    """
    Delete an object from NetBox by its ID.
    
    Args:
        object_type: String representing the NetBox object type (e.g. "devices", "ip-addresses")
        object_id: The numeric ID of the object to delete
    
    Returns:
        None if successful, raises an exception if the deletion fails
    
    Example:
    To delete a device with ID 123:
    delete_object("devices", 123)
    """
    # Validate object_type exists in mapping
    if object_type not in NETBOX_OBJECT_TYPES:
        valid_types = "\n".join(f"- {t}" for t in sorted(NETBOX_OBJECT_TYPES.keys()))
        raise ValueError(f"Invalid object_type. Must be one of:\n{valid_types}")
        
    # Get API endpoint from mapping
    endpoint = f"{NETBOX_OBJECT_TYPES[object_type]}"
    
    # Make API call to delete object
    return netbox.delete(endpoint)

@mcp.prompt(
    name="netbox-mcp",
    description="NetBox MCP (Multi-Channel Protocol) server for managing NetBox objects",
)
def netbox_mcp():
    return """
    Main function to handle NetBox MCP (Multi-Channel Protocol) server.
    
    Available Tools:
    
    1. get_objects(object_type: str, filters: dict)
       - Retrieves objects from NetBox based on type and filters
       - object_type: Type of object to retrieve (e.g., "devices", "ip-addresses")
       - filters: Dictionary of filter criteria
       - Returns a list of matching objects
    
    2. get_object_by_id(object_type: str, object_id: int)
       - Gets detailed information about a specific NetBox object
       - object_type: Type of object to retrieve
       - object_id: Numeric ID of the object
       - Returns complete object details
    
    3. get_changelogs(filters: dict)
       - Retrieves object change records (changelogs)
       - filters: Dictionary of filter criteria
       - Returns list of changelog entries
       - Useful for tracking changes and auditing
    
    4. create_object(object_type: str, data: dict)
       - Creates a new object in NetBox
       - object_type: Type of object to create
       - data: Dictionary containing object data
       - Returns the created object
    
    5. update_object(object_type: str, object_id: int, data: dict)
       - Updates an existing object
       - object_type: Type of object to update
       - object_id: ID of object to update
       - data: Dictionary of fields to update
       - Returns the updated object
    
    6. delete_object(object_type: str, object_id: int)
       - Deletes an object from NetBox
       - object_type: Type of object to delete
       - object_id: ID of object to delete
       - Returns None if successful
    
    Supported Object Types:
    - DCIM: devices, interfaces, sites, racks, etc.
    - IPAM: ip-addresses, prefixes, vlans, vrfs, etc.
    - Circuits: circuits, providers, etc.
    - Virtualization: virtual-machines, clusters, etc.
    - Tenancy: tenants, contacts, etc.
    - VPN: tunnels, policies, etc.
    - Wireless: wireless-lans, wireless-links, etc.
    
    Example Usage:
    1. To get devices on netbox with Year of investment in 3/2022:
        # First, search for devices with the "Year of investment" field
        devices = get_objects("devices", {"cf_year_of_investment": 3/2022})
       
        # If no devices are found, search for devices with a custom field "Year of investment"
        if not devices:
            devices = get_objects("devices", {"year_of_investment": 3/2022})
        
        # Returns the list of matching devices
        return devices
    
    2. To get all devices in a site:
        # First, find the site by name
        site = get_objects("sites", {"name": "site-name"})

        # Then, get devices in that site
        devices = get_objects("devices", {"site_id": site[0]["id"]})
        
        # Returns the list of devices in the specified site
        return devices 

    3. To get devices with Year of investment in 3/2022:
        # First, search for devices with the "Year of investment" field
        devices = get_objects("devices", {"cf_year_of_investment": 3/2022})
       
        # If no devices are found, search for devices with a custom field "Year of investment"
        if not devices:
            devices = get_objects("devices", {"year_of_investment": 3/2022})
        
        # Returns the list of matching devices
        return devices

    4. To get all devices on netbox:
        devices = get_objects("devices", {})
        return devices

    5. To get a specific device:
        get_object_by_id("devices", 123)

    6. To create a new device:
        create_object("devices", {
            "name": "router1",
            "device_type": 1,
            "device_role": 1,
            "site": 1,
            "status": "active"
        })
    
    7. To update a device:
        # First, find the device by name
        devices = get_objects("devices", {"name": "router1"})
        
        # If multiple devices are found, you can use the first one
        if devices and len(devices) > 0:
            device_id = devices[0]["id"]
            
            # Then update the device using its ID
            update_object("devices", device_id, {
                "name": "new-router-name",
                "status": "maintenance",
                "comments": "Updated via MCP"
            })
        else:
            print("No device found with name 'router1'")
      
    8. To delete a device:
        delete_object("devices", 123)
    
    9. To view changes:
        get_changelogs({
            "changed_object_type": "dcim.device",
            "changed_object_id": 123
        })
    
        
    Remember to:
    - Always validate object types before making requests
    - Check required fields for object creation
    - Use appropriate filters to narrow down results
    - Handle errors gracefully
    - Consider the impact of changes before making them
    
    """



if __name__ == "__main__":
    # Load NetBox configuration from environment variables
    netbox_url = os.getenv("NETBOX_URL")
    netbox_token = os.getenv("NETBOX_TOKEN")
    
    if not netbox_url or not netbox_token:
        raise ValueError("NETBOX_URL and NETBOX_TOKEN environment variables must be set")
    
    # Initialize NetBox client
    netbox = NetBoxRestClient(url=netbox_url, token=netbox_token)
    
    #mcp.run(transport="stdio")
    mcp.run(transport="sse")