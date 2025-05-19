from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from abc import ABC, abstractmethod
import re

# --- Generic Product Listing Data Structure ---
@dataclass
class GenericProductListing:
    """
    A generic representation of a product listing, holding common information.
    """
    product_id: str
    title: str
    description: str
    images: List[str]  # List of image URLs
    price: float
    currency: str = "INR"
    category_generic: str = "General" # A broad category
    brand: Optional[str] = None
    sku: Optional[str] = None # Stock Keeping Unit
    stock_quantity: Optional[int] = None
    attributes: Dict[str, Any] = field(default_factory=dict) # e.g., {"color": "Red", "size": "M", "material": "Cotton"}
    keywords: List[str] = field(default_factory=list)
    
    # Fields that might be more specific but useful to have at a generic level for transformation
    bullet_points: List[str] = field(default_factory=list) # Often used by Amazon, Flipkart (key features)
    model_name: Optional[str] = None
    part_number: Optional[str] = None
    weight_grams: Optional[float] = None
    dimensions_cm: Optional[Dict[str, float]] = field(default_factory=dict) # e.g., {"length": 10, "width": 5, "height": 2}
    country_of_origin: Optional[str] = "India" # Common requirement
    hsn_code: Optional[str] = None # Harmonized System of Nomenclature code for tax purposes

    def get_attribute(self, key: str, default: Any = None) -> Any:
        return self.attributes.get(key, default)

# --- Abstract Marketplace Formatter ---
class MarketplaceListingFormatter(ABC):
    """
    Abstract base class for marketplace-specific listing formatters.
    """
    def __init__(self, marketplace_name: str):
        self.marketplace_name = marketplace_name

    @abstractmethod
    def format_listing(self, generic_listing: GenericProductListing) -> Dict[str, Any]:
        """
        Converts a GenericProductListing into a dictionary structured for the specific marketplace.

        Args:
            generic_listing (GenericProductListing): The product listing data in a generic format.

        Returns:
            Dict[str, Any]: A dictionary representing the listing in the marketplace-specific format.
        """
        pass

    def _clean_html(self, text: str) -> str:
        """Utility to remove HTML tags."""
        if text:
            return re.sub(r'<[^>]+>', '', text)
        return ""

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Utility to truncate text to a maximum length."""
        if text and len(text) > max_length:
            return text[:max_length].rsplit(' ', 1)[0] + "..." # Truncate at last space
        return text if text else ""

# --- Concrete Marketplace Formatters ---

class AmazonListingFormatter(MarketplaceListingFormatter):
    """
    Formats a listing for Amazon.
    """
    MAX_TITLE_LENGTH = 200 # Example constraint
    MAX_BULLET_POINTS = 5
    MAX_BULLET_POINT_LENGTH = 500 # Example constraint

    def __init__(self):
        super().__init__("Amazon")

    def format_listing(self, generic_listing: GenericProductListing) -> Dict[str, Any]:
        amazon_listing = {
            "feed_product_type": "product", # This can vary based on category
            "item_sku": generic_listing.sku or generic_listing.product_id,
            "external_product_id": generic_listing.product_id,
            "external_product_id_type": "ASIN" if len(generic_listing.product_id) == 10 and generic_listing.product_id.isalnum() else "UPC", # Simplified logic
            "item_name": self._truncate_text(generic_listing.title, self.MAX_TITLE_LENGTH),
            "brand_name": generic_listing.brand,
            "manufacturer": generic_listing.brand, # Often same as brand
            "part_number": generic_listing.part_number or generic_listing.model_name,
            "product_description": self._clean_html(generic_listing.description),
            "standard_price": generic_listing.price,
            "currency": generic_listing.currency,
            "quantity": generic_listing.stock_quantity,
            "main_image_url": generic_listing.images[0] if generic_listing.images else None,
            "other_image_urls": generic_listing.images[1:9] if generic_listing.images and len(generic_listing.images) > 1 else [], # Amazon allows up to 8 other images
            "bullet_points": [self._truncate_text(bp, self.MAX_BULLET_POINT_LENGTH) for bp in generic_listing.bullet_points[:self.MAX_BULLET_POINTS]],
            "generic_keywords": ", ".join(generic_listing.keywords[:5]), # Amazon's 'search_terms' or 'generic_keywords'
            "item_type_keyword": generic_listing.category_generic, # Needs mapping to Amazon's item_type
            "recommended_browse_nodes": [], # This would require a category mapping system
            "attributes": {}, # For specific Amazon attributes like color_map, size_map
            "country_of_origin": generic_listing.country_of_origin,
        }

        # Populate Amazon-specific attributes from generic attributes
        if generic_listing.get_attribute("color"):
            amazon_listing["attributes"]["color_name"] = generic_listing.get_attribute("color")
        if generic_listing.get_attribute("size"):
            amazon_listing["attributes"]["size_name"] = generic_listing.get_attribute("size")
        if generic_listing.get_attribute("material"):
            amazon_listing["attributes"]["material_type"] = generic_listing.get_attribute("material")
        
        if generic_listing.weight_grams:
             amazon_listing["item_weight"] = { "value": generic_listing.weight_grams / 1000, "unit": "KG"} # Amazon often wants unit

        # Placeholder for variation data if applicable
        # amazon_listing["variation_data"] = {...}

        return amazon_listing

class FlipkartListingFormatter(MarketplaceListingFormatter):
    """
    Formats a listing for Flipkart.
    """
    MAX_TITLE_LENGTH = 120 # Example constraint
    MAX_KEY_FEATURES = 5
    MAX_FEATURE_LENGTH = 255 # Example constraint

    def __init__(self):
        super().__init__("Flipkart")

    def format_listing(self, generic_listing: GenericProductListing) -> Dict[str, Any]:
        flipkart_listing = {
            "sku_id": generic_listing.sku or generic_listing.product_id,
            "product_id": generic_listing.product_id, # Your internal ID
            "title": self._truncate_text(generic_listing.title, self.MAX_TITLE_LENGTH),
            "description": self._clean_html(generic_listing.description), # Flipkart might allow some HTML
            "brand": generic_listing.brand,
            "images": generic_listing.images[:8], # Flipkart allows up to 8 images
            "mrp": generic_listing.price * 1.1, # Example: MRP might be higher than selling price
            "selling_price": generic_listing.price,
            "currency": generic_listing.currency,
            "stock_count": generic_listing.stock_quantity,
            "flipkart_category_id": None, # Requires mapping from generic_listing.category_generic
            "attributes": { # Flipkart has a specific structure for attributes/specifications
                "key_features": [self._truncate_text(bp, self.MAX_FEATURE_LENGTH) for bp in generic_listing.bullet_points[:self.MAX_KEY_FEATURES]],
                "model_name": generic_listing.model_name,
                "part_number": generic_listing.part_number,
                "color": generic_listing.get_attribute("color"),
                "size": generic_listing.get_attribute("size"),
                "material": generic_listing.get_attribute("material"),
                # Add other common Flipkart specifications based on category
            },
            "shipping_details": {
                "weight_grams": generic_listing.weight_grams,
                "length_cm": generic_listing.dimensions_cm.get("length"),
                "breadth_cm": generic_listing.dimensions_cm.get("width"),
                "height_cm": generic_listing.dimensions_cm.get("height"),
                "country_of_origin": generic_listing.country_of_origin,
                "hsn": generic_listing.hsn_code,
            },
            "search_keywords": generic_listing.keywords,
            "fulfillment_by": "SELLER", # or "FLIPKART_ADVANTAGE"
        }
        
        # Filter out None values from attributes and shipping_details for cleaner output
        flipkart_listing["attributes"] = {k: v for k, v in flipkart_listing["attributes"].items() if v is not None}
        flipkart_listing["shipping_details"] = {k: v for k, v in flipkart_listing["shipping_details"].items() if v is not None}

        return flipkart_listing

class MeeshoListingFormatter(MarketplaceListingFormatter):
    """
    Formats a listing for Meesho.
    """
    MAX_TITLE_LENGTH = 100 # Example constraint
    MAX_DESCRIPTION_WORDS = 150 # Example constraint

    def __init__(self):
        super().__init__("Meesho")

    def _word_truncate(self, text: str, max_words: int) -> str:
        if not text: return ""
        words = text.split()
        if len(words) > max_words:
            return " ".join(words[:max_words]) + "..."
        return text

    def format_listing(self, generic_listing: GenericProductListing) -> Dict[str, Any]:
        # Meesho often focuses on single products and simpler structures
        # They also have a strong emphasis on supplier-side information which isn't part of this generic listing.
        meesho_listing = {
            "product_name": self._truncate_text(generic_listing.title, self.MAX_TITLE_LENGTH),
            "category_id": None, # Requires mapping from generic_listing.category_generic
            "supplier_sku_id": generic_listing.sku or generic_listing.product_id,
            "product_description": self._word_truncate(self._clean_html(generic_listing.description), self.MAX_DESCRIPTION_WORDS),
            "images": generic_listing.images[:5], # Meesho typically allows around 5 images
            "price_per_unit": generic_listing.price, # Meesho's term for selling price
            "mrp_per_unit": generic_listing.price * 1.2, # Example: MRP
            "inventory_count": generic_listing.stock_quantity,
            "product_weight_gm": generic_listing.weight_grams,
            "country_of_origin": generic_listing.country_of_origin,
            "hsn_code": generic_listing.hsn_code,
            "attributes": [], # Meesho often uses a list of attribute key-value pairs
        }

        # Convert generic attributes to Meesho's list format
        for key, value in generic_listing.attributes.items():
            if value: # Only add if value exists
                meesho_listing["attributes"].append({"name": key.replace("_", " ").title(), "value": str(value)})
        
        if generic_listing.brand:
             meesho_listing["attributes"].append({"name": "Brand", "value": generic_listing.brand})


        return meesho_listing

# --- Example Usage ---
if __name__ == "__main__":
    # Create a generic product listing
    product_data = GenericProductListing(
        product_id="PROD12345",
        title="High-Quality Cotton T-Shirt with Cool Graphic Print - Limited Edition",
        description="<p>Experience ultimate comfort with our <b>100% premium cotton</b> t-shirt. "
                    "Features a unique, eye-catching graphic print designed by artists. "
                    "Perfect for casual wear, parties, or as a gift. Durable and machine washable.</p>"
                    "Available in multiple sizes. Grab this limited edition tee before it's gone!",
        images=["http://example.com/image1.jpg", "http://example.com/image2.jpg", "http://example.com/image3.jpg", "http://example.com/image4.jpg", "http://example.com/image5.jpg", "http://example.com/image6.jpg"],
        price=799.00,
        currency="INR",
        category_generic="Apparel/Men/T-Shirts",
        brand="CoolThreads Co.",
        sku="CT-GRPH-TEE-M-BLK",
        stock_quantity=150,
        attributes={"color": "Black", "size": "M", "material": "100% Cotton", "sleeve_type": "Half Sleeve"},
        keywords=["cotton t-shirt", "graphic tee", "men's apparel", "casual wear", "limited edition"],
        bullet_points=[
            "PREMIUM QUALITY: Made from 100% pure, breathable cotton for all-day comfort.",
            "UNIQUE DESIGN: Features an exclusive graphic print not found anywhere else.",
            "VERSATILE WEAR: Ideal for casual outings, college, or pairing with jeans.",
            "DURABLE & EASY CARE: Machine washable and built to last.",
            "PERFECT FIT: Available in Medium size (refer to size chart)."
        ],
        model_name="GraphicTee-V2",
        part_number="GT-V2-M-BLK",
        weight_grams=180.0,
        dimensions_cm={"length": 70, "width": 50, "height": 1}, # Flat packed
        country_of_origin="India",
        hsn_code="61091000"
    )

    # Instantiate formatters
    amazon_formatter = AmazonListingFormatter()
    flipkart_formatter = FlipkartListingFormatter()
    meesho_formatter = MeeshoListingFormatter()

    # Format for each marketplace
    print("--- Amazon Formatted Listing ---")
    amazon_formatted = amazon_formatter.format_listing(product_data)
    for key, value in amazon_formatted.items():
        print(f"  {key}: {value}")

    print("\n--- Flipkart Formatted Listing ---")
    flipkart_formatted = flipkart_formatter.format_listing(product_data)
    for key, value in flipkart_formatted.items():
        print(f"  {key}: {value}")

    print("\n--- Meesho Formatted Listing ---")
    meesho_formatted = meesho_formatter.format_listing(product_data)
    for key, value in meesho_formatted.items():
        print(f"  {key}: {value}")

    # Example of a simpler product
    simple_product = GenericProductListing(
        product_id="SIMPLE001",
        title="Basic Blue Pen",
        description="A reliable blue ballpoint pen for everyday writing.",
        images=["http://example.com/pen.jpg"],
        price=10.00,
        brand="PenCo",
        sku="PCO-BLU-PEN",
        stock_quantity=1000,
        attributes={"color": "Blue", "type": "Ballpoint"},
        keywords=["pen", "blue pen", "stationery"],
        weight_grams=15.0
    )
    print("\n--- Amazon Formatted Simple Listing ---")
    amazon_simple_formatted = amazon_formatter.format_listing(simple_product)
    for key, value in amazon_simple_formatted.items():
        print(f"  {key}: {value}")
