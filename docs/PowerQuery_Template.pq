// Certify Intel - Power Query M Code Template
// Connect your Excel dashboard to the Certify Intel API
// Created: January 2026

// =============================================================================
// OPTION 1: Direct JSON API Connection
// =============================================================================
// Use this if you want real-time data from the API

let
    // CHANGE THIS: Set your API server URL
    ServerUrl = "http://localhost:8000",
    
    // Fetch competitor data from API
    Source = Json.Document(
        Web.Contents(
            ServerUrl & "/api/export/json",
            [
                Headers = [
                    #"Accept" = "application/json",
                    #"Content-Type" = "application/json"
                ],
                Timeout = #duration(0, 0, 2, 0) // 2 minute timeout
            ]
        )
    ),
    
    // Extract the competitors list
    CompetitorsList = Source[competitors],
    
    // Convert to table
    ToTable = Table.FromList(CompetitorsList, Splitter.SplitByNothing(), null, null, ExtraValues.Error),
    
    // Expand the record column
    ExpandedTable = Table.ExpandRecordColumn(
        ToTable, 
        "Column1", 
        {
            "name", "website", "status", "threat_level", "last_updated",
            "notes", "data_quality_score", "pricing_model", "base_price", "price_unit",
            "product_categories", "key_features", "integration_partners", "certifications",
            "target_segments", "customer_size_focus", "geographic_focus", "customer_count",
            "customer_acquisition_rate", "key_customers", "g2_rating", "employee_count",
            "employee_growth_rate", "year_founded", "headquarters", "funding_total",
            "latest_round", "pe_vc_backers", "website_traffic", "social_following",
            "recent_launches", "news_mentions"
        }
    ),
    
    // Rename columns to match dashboard format
    RenamedColumns = Table.RenameColumns(ExpandedTable, {
        {"name", "Competitor Name"},
        {"website", "Website"},
        {"status", "Status"},
        {"threat_level", "Threat Level"},
        {"last_updated", "Last Updated"},
        {"pricing_model", "Pricing Model"},
        {"base_price", "Base Price"},
        {"price_unit", "Price Unit"},
        {"product_categories", "Product Categories"},
        {"key_features", "Key Features"},
        {"integration_partners", "Integration Partners"},
        {"certifications", "Certifications"},
        {"target_segments", "Target Segments"},
        {"customer_size_focus", "Customer Size Focus"},
        {"geographic_focus", "Geographic Focus"},
        {"customer_count", "Customer Count"},
        {"customer_acquisition_rate", "Customer Acquisition Rate"},
        {"key_customers", "Key Customers"},
        {"g2_rating", "G2 Rating"},
        {"employee_count", "Employee Count"},
        {"employee_growth_rate", "Employee Growth Rate"},
        {"year_founded", "Year Founded"},
        {"headquarters", "Headquarters"},
        {"funding_total", "Funding Total"},
        {"latest_round", "Latest Round"},
        {"pe_vc_backers", "PE/VC Backers"},
        {"website_traffic", "Website Traffic"},
        {"social_following", "Social Following"},
        {"recent_launches", "Recent Launches"},
        {"news_mentions", "News Mentions"}
    }),
    
    // Set data types
    TypedTable = Table.TransformColumnTypes(RenamedColumns, {
        {"Competitor Name", type text},
        {"Website", type text},
        {"Status", type text},
        {"Threat Level", type text},
        {"Last Updated", type datetime},
        {"G2 Rating", type number}
    })
    
in
    TypedTable


// =============================================================================
// OPTION 2: Direct Excel File Connection (Simpler)
// =============================================================================
// Use this if you prefer downloading the Excel file

/*
let
    // CHANGE THIS: Download the Excel file and save it locally
    Source = Excel.Workbook(
        File.Contents("C:\Path\To\certify_intel_export.xlsx"), 
        null, 
        true
    ),
    
    // Get the Competitors sheet
    CompetitorsSheet = Source{[Item="Competitors", Kind="Sheet"]}[Data],
    
    // Promote headers
    PromotedHeaders = Table.PromoteHeaders(CompetitorsSheet, [PromoteAllScalars=true])
    
in
    PromotedHeaders
*/


// =============================================================================
// OPTION 3: Dashboard Stats Query
// =============================================================================
// Get summary statistics for dashboard cards

/*
let
    ServerUrl = "http://localhost:8000",
    
    Source = Json.Document(
        Web.Contents(ServerUrl & "/api/dashboard/stats")
    ),
    
    StatsTable = Record.ToTable(Source),
    
    PivotedTable = Table.Pivot(
        StatsTable, 
        List.Distinct(StatsTable[Name]), 
        "Name", 
        "Value"
    )
    
in
    PivotedTable
*/
