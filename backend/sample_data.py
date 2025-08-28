"""
Sample data generator for Apple Annual Reports QA System.
Creates mock Apple annual report data for testing purposes.
"""

import os
import json
from datetime import datetime

def create_sample_apple_reports():
    """Create sample Apple annual report data."""
    
    # Sample Apple annual report data for different years
    sample_reports = {
        2023: {
            "title": "Apple Inc. Annual Report 2023",
            "revenue": "$394.33 billion",
            "net_income": "$96.99 billion",
            "key_highlights": [
                "iPhone revenue: $200.58 billion",
                "Mac revenue: $29.36 billion", 
                "iPad revenue: $28.28 billion",
                "Wearables, Home and Accessories: $38.36 billion",
                "Services revenue: $85.20 billion"
            ],
            "geographic_breakdown": {
                "Americas": "$169.56 billion",
                "Europe": "$95.02 billion",
                "Greater China": "$72.56 billion",
                "Japan": "$28.25 billion",
                "Rest of Asia Pacific": "$28.94 billion"
            },
            "environmental_goals": "Carbon neutral for corporate operations since 2020",
            "innovation_focus": "Continued investment in AI, AR/VR, and autonomous systems"
        },
        2022: {
            "title": "Apple Inc. Annual Report 2022", 
            "revenue": "$394.33 billion",
            "net_income": "$99.80 billion",
            "key_highlights": [
                "iPhone revenue: $205.55 billion",
                "Mac revenue: $40.18 billion",
                "iPad revenue: $29.29 billion", 
                "Wearables, Home and Accessories: $41.20 billion",
                "Services revenue: $78.13 billion"
            ],
            "geographic_breakdown": {
                "Americas": "$169.56 billion",
                "Europe": "$95.02 billion", 
                "Greater China": "$74.72 billion",
                "Japan": "$25.94 billion",
                "Rest of Asia Pacific": "$29.09 billion"
            },
            "supply_chain": "Continued diversification and resilience building",
            "privacy_focus": "Enhanced privacy features across all products"
        },
        2021: {
            "title": "Apple Inc. Annual Report 2021",
            "revenue": "$365.82 billion", 
            "net_income": "$94.68 billion",
            "key_highlights": [
                "iPhone revenue: $191.97 billion",
                "Mac revenue: $35.19 billion",
                "iPad revenue: $31.86 billion",
                "Wearables, Home and Accessories: $38.37 billion", 
                "Services revenue: $68.43 billion"
            ],
            "geographic_breakdown": {
                "Americas": "$153.68 billion",
                "Europe": "$82.73 billion",
                "Greater China": "$68.37 billion", 
                "Japan": "$25.82 billion",
                "Rest of Asia Pacific": "$35.22 billion"
            },
            "chip_transition": "Completed transition to Apple Silicon for Mac lineup",
            "privacy_leadership": "Introduced App Tracking Transparency"
        }
    }
    
    # Create data directory if it doesn't exist
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Create sample PDF-like text files (simulating processed PDF content)
    for year, data in sample_reports.items():
        filename = f"apple_annual_report_{year}.txt"
        filepath = os.path.join(data_dir, filename)
        
        content = f"""
{data['title']}

EXECUTIVE SUMMARY

Apple Inc. reported record-breaking financial results for fiscal year {year}, demonstrating the company's continued innovation and market leadership.

FINANCIAL HIGHLIGHTS

Total Revenue: {data['revenue']}
Net Income: {data['net_income']}

PRODUCT PERFORMANCE

{chr(10).join([f"• {highlight}" for highlight in data['key_highlights']])}

GEOGRAPHIC PERFORMANCE

{chr(10).join([f"• {region}: {revenue}" for region, revenue in data['geographic_breakdown'].items()])}

STRATEGIC INITIATIVES

{chr(10).join([f"• {key.replace('_', ' ').title()}: {value}" for key, value in data.items() if key not in ['title', 'revenue', 'net_income', 'key_highlights', 'geographic_breakdown']])}

INNOVATION AND R&D

Apple continues to invest heavily in research and development, focusing on breakthrough technologies that will define the future of personal computing and mobile communications.

SUSTAINABILITY

Apple remains committed to environmental responsibility, with ongoing efforts to reduce carbon footprint and transition to renewable energy sources across its supply chain.

CONCLUSION

Fiscal year {year} represents another successful year for Apple, with strong performance across all product categories and continued growth in services revenue.
        """
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        
        print(f"Created sample data for year {year}: {filename}")
    
    print(f"\nSample data created in {data_dir}/ directory")
    print("You can now initialize the QA system with this data.")

if __name__ == "__main__":
    create_sample_apple_reports()
