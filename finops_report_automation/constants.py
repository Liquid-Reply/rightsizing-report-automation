"""
Module that holds all constants variables such as:
- mapping between json keys to column header names
- file paths

:license: AGPL v3, see LICENSE for more details
:copyright: 2022 Liquid Reply GmbH
"""

GENERAL_SHEET_CONFIGURATION = {
    "column_mapping": {
        "vendorAccountId": "Account ID",
        "vendorAccountName": "Account Name",
        "name": "Resource type",
        "recommendations_action": "Recommendation type",
        "highestOptimization": "Highest single resource optimiziation (monthly $)",
        "monthlySavings": "Monthly savings potential in $ (all rightsizing options applied)",
        "annualSavings": "Annual Saving Potential*",
        "amortizedCost": "Total Cloud Costs of month ($), amortized, last 30 days",
        "relationPotentialSavings": "Relation of potential savings ($) to total costs ($) in % (current month)",
        "message": "Recommendation basis"
    },
}

EC2_CONFIGURATION = {
    "recommendation_mapping": {
        "recommendations_action": "Recommendation",
        "recommendations_nodeType": "New Instance Type",
        "recommendations_savings": "Savings",
        "recommendations_risk": "Risk assessment for recommendation",
    },
    "column_mapping": {
        "resourceIdentifier": "Resource ID",
        "name": "Resource Name",
        "vendorAccountId": "Account ID",
        "availabilityZone": "Availability Zone",
        "region": "Region",
        "os": "Operating System",
        "nodeType": "Instance Type - Current",
        "currencyCode": "Currency Code",
        "unitPrice": "Unit Price - Current",
        "totalSpend": "Cost",
    },
    "account_name_mapping": {
        "vendorAccountId": "Account ID",
        "vendorAccountName": "Account Name"
    },
    "account_name_column_mapping": {
        "vendorAccountName": "Account Name"
    },
    "recommendation_grouping": {
        "groupby": ["vendorAccountId", "recommendations_savings"],
        "selection": ["vendorAccountId", "nodeType", "recommendations_nodeType", "recommendations_savings"],
    },
    "messages": {
        "terminate": {
            "zero": "Currently no termination recommendations >50$/month for your accounts available.",
            "one": "{vendorAccountId}: 1 termination recommendation was identified: Instance {nodeType} " +
            "is underutilized based on the analysis of the last 10 days.",
            "moreThanOne": "{vendorAccountId}: {count} termination recommendations were identified. " +
            "Recommended Action with highest potential: Instance {nodeType} " +
            "is underutilized based on the analysis of the last 10 days."
        },
        "rightsize": {
            "zero": "Currently no rightsizing recommendations >50$/month for your accounts available.",
            "one": "{vendorAccountId}: 1 rightsizing recommendation was identified: Change instance {nodeType} to {recommendations_nodeType}",
            "moreThanOne": "{vendorAccountId}: {count} rightsizing recommendations were identified:  " +
            "Recommended Action with highest potential: Change instance {nodeType} to {recommendations_nodeType}"
        },
    }
}

EBS_CONFIGURATION = {
    "recommendation_mapping": {
        "recommendations_action": "Recommendation",
        "recommendations_volumeType": "Volume type recommended",
        "recommendations_savings": "Savings",
        "recommendations_risk": "Risk assessment for recommendation",
    },
    "column_mapping": {
        "resourceIdentifier": "Resource ID",
        "name": "Resource Name",
        "vendorAccountId": "Account ID",
        "availabilityZone": "Availability Zone",
        "region": "Region",
        "state": "State",
        "volumeType": "Volume",
        "currencyCode": "Currency Code",
        "unitPrice": "Unit Price - Current",
        "totalSpend": "Cost",
    },
    "account_name_mapping": {
        "vendorAccountId": "Account ID",
        "vendorAccountName": "Account Name"
    },
    "account_name_column_mapping": {
        "vendorAccountName": "Account Name"
    },
    "recommendation_grouping": {
        "groupby": ["vendorAccountId", "recommendations_savings"],
        "selection": ["vendorAccountId", "volumeType", "recommendations_volumeType", "recommendations_savings"],
    },
    "messages": {
        "terminate": {
            "zero": "Currently no termination recommendations >50$/month for your accounts available.",
            "one": "{vendorAccountId}: 1 termination recommendation was identified: Volume {volumeType} " +
            "is underutilized based on the analysis of the last 10 days.",
            "moreThanOne": "{vendorAccountId}: {count} termination recommendations were identified. " +
            "Recommended Action with highest potential: Volume {volumeType} " +
            "is underutilized based on the analysis of the last 10 days."
        },
        "rightsize": {
            "zero": "Currently no rightsizing recommendations >50$/month for your accounts available.",
            "one": "{vendorAccountId}: 1 rightsizing recommendation was identified: Change volume {volumeType} to {recommendations_volumeType}",
            "moreThanOne": "{vendorAccountId}: {count} rightsizing recommendations were identified:  " +
            "Recommended Action with highest potential: Change volume {volumeType} to {recommendations_volumeType}"
        },
    }
}


S3_CONFIGURATION = {
    "recommendation_mapping": {
        "recommendations_action": "Recommendation",
        "recommendations_resourceType": "Storage Class recommended",
        "recommendations_savings": "Savings",
        "recommendations_risk": "Risk assessment for recommendation",
    },
    "column_mapping": {
        "resourceIdentifier": "Resource ID",
        "name": "Resource Name",
        "vendorAccountId": "Account ID",
        "resourceType": "Storage Class",
        "currencyCode": "Currency Code",
        "totalSpend": "Cost",
    },
    "account_name_mapping": {
        "vendorAccountId": "Account ID",
        "vendorAccountName": "Account Name"
    },
    "account_name_column_mapping": {
        "vendorAccountName": "Account Name"
    },
    "recommendation_grouping": {
        "groupby": ["vendorAccountId", "recommendations_savings"],
        "selection": ["vendorAccountId", "resourceType", "recommendations_resourceType", "recommendations_savings"],
    },
    "messages": {
        "terminate": {
            "zero": "Currently no termination recommendations >50$/month for your accounts available.",
            "one": "{vendorAccountId}: 1 termination recommendation was identified: Resource {resourceType} " +
            "is underutilized based on the analysis of the last 10 days.",
            "moreThanOne": "{vendorAccountId}: {count} termination recommendations were identified. " +
            "Recommended Action with highest potential: Resource {resourceType} " +
            "is underutilized based on the analysis of the last 10 days."
        },
        "rightsize": {
            "zero": "Currently no rightsizing recommendations >50$/month for your accounts available.",
            "one": "{vendorAccountId}: 1 rightsizing recommendation was identified: Change storage class {resourceType} to {recommendations_resourceType}",
            "moreThanOne": "{vendorAccountId}: {count} rightsizing recommendations were identified:  " +
            "Recommended Action with highest potential: Change storage class {resourceType} to {recommendations_resourceType}"
        },
    }
}


RDS_CONFIGURATION = {
    "recommendation_mapping": {
        "recommendations_action": "Recommendation",
        "recommendations_nodeType": "Instance Type - Recommended",
        "recommendations_risk": "Risk assessment for recommendation",
    },
    "storageRecommendation_mapping": {
        "storagerecommendations_action": "Recommendation",
        "storagerecommendations_storageType": "Storage type - Recommended",
    },
    "column_mapping": {
        "clusterIdentifier": "Cluster ID",
        "resourceIdentifier": "Resource ID",
        "name": "Resource Name",
        "vendorAccountId": "Account ID",
        "clusterRole": "Cluster Role",
        "databaseEngine": "Engine",
        "nodeType": "Instance Type - Current",
        "storageType": "Storage Type - Current",
        "currencyCode": "Currency Code",
        "unitPrice": "Effective Rate - Current",
        "totalSpend": "Cost",
        "topSavings": "Savings"
    },
    "account_name_mapping": {
        "vendorAccountId": "Account ID",
        "vendorAccountName": "Account Name"
    },
    "account_name_column_mapping": {
        "vendorAccountName": "Account Name"
    },
    "recommendation_grouping": {
        "groupby": ["vendorAccountId", "topSavings"],
        "selection": [
            "vendorAccountId",
            "nodeType",
            "recommendations_nodeType",
            "topSavings",
            "storagerecommendations_storageType",
            "storagerecommendations_action"
        ]
    },
    "messages": {
        "terminate": {
            "zero": "Currently no termination recommendations >50$/month for your accounts available.",
            "one": "{vendorAccountId}: 1 termination recommendation was identified: Instance {nodeType} " +
            "is underutilized based on the analysis of the last 10 days.",
            "moreThanOne": "{vendorAccountId}: {count} termination recommendations were identified. " +
            "Recommended Action with highest potential: Instance {nodeType} " +
            "is underutilized based on the analysis of the last 10 days."
        },
        "rightsize": {
            "zero": "Currently no rightsizing recommendations >50$/month for your accounts available.",
            "one": "{vendorAccountId}: 1 rightsizing recommendation was identified: Change instance {nodeType} to {recommendations_nodeType} {storage}",
            "moreThanOne": "{vendorAccountId}: {count} rightsizing recommendations were identified:  " +
            "Recommended Action with highest potential: Change instance {nodeType} to {recommendations_nodeType} {storage}",
        },
        "storage_message": {
            "terminate": "and terminate the storage.",
            "noaction": "while keeping the current storage.",
            "rightsize": "and rightsize the current storage."
        }
    }
}
