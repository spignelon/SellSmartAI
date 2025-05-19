class AmazonListing:
    def _init_(self, title, keywords, bullet_points, description, images, backend_keywords):
        self.title = title
        self.keywords = keywords
        self.bullet_points = bullet_points
        self.description = description
        self.images = images
        self.backend_keywords = backend_keywords

    def calculate_seo_score(self):
        score = 0
        if 50 <= len(self.title) <= 200:
            score += 2
        if any(kw.lower() in self.title.lower() for kw in self.keywords):
            score += 2
        if len(self.bullet_points) >= 5:
            score += 2
        if len(self.description) > 100:
            score += 1
        if len(self.images) >= 3:
            score += 2
        if len(self.backend_keywords) > 0:
            score += 1
        return round(score, 1), "/10"


class FlipkartListing:
    def _init_(self, title, brand, category, description, images):
        self.title = title
        self.brand = brand
        self.category = category
        self.description = description
        self.images = images

    def is_compliant(self):
        return (
            bool(self.title) and
            bool(self.brand) and
            bool(self.category) and
            len(self.description) > 50 and
            len(self.images) >= 1
        )


class FlipkartComplianceChecker:
    def _init_(self, listings):
        self.listings = listings

    def calculate_compliance(self):
        compliant_count = sum(1 for listing in self.listings if listing.is_compliant())
        total = len(self.listings)
        return round((compliant_count / total) * 100, 2) if total else 0


class MeeshoListing:
    def _init_(self, impressions, clicks):
        self.impressions = impressions
        self.clicks = clicks

    def calculate_ctr(self):
        if self.impressions == 0:
            return 0.0
        return round((self.clicks / self.impressions) * 100, 2)


# Optional: Test block to run if executed directly
if __name__ == "__main__":
    # Test Amazon SEO Score
    amazon_product = AmazonListing(
        title="Stylish Casual Shirt for Men - Slim Fit",
        keywords=["shirt", "casual", "men"],
        bullet_points=["Cotton fabric", "Slim fit", "All sizes", "Machine washable", "Trendy design"],
        description="This casual shirt is perfect for all occasions with a stylish slim fit design.",
        images=["img1.jpg", "img2.jpg", "img3.jpg"],
        backend_keywords=["slim fit shirt", "cotton shirt"]
    )
    print("Amazon SEO Score:", amazon_product.calculate_seo_score())

    # Test Flipkart Compliance
    flipkart_listings = [
        FlipkartListing("Shirt", "BrandX", "Men > Clothing", "Nice cotton shirt suitable for all seasons and types of weather.", ["img1.jpg"]),
        FlipkartListing("", "BrandY", "Women > Footwear", "", []),  # Non-compliant
        FlipkartListing("Sneakers", "BrandZ", "Shoes", "Comfortable sneakers with soft sole for daily use.", ["img1.jpg", "img2.jpg"])
    ]
    checker = FlipkartComplianceChecker(flipkart_listings)
    print("Flipkart Compliance Score:", checker.calculate_compliance(), "%")

    # Test Meesho CTR
    meesho_listing = MeeshoListing(impressions=1000, clicks=48)
    print("Meesho CTR:", meesho_listing.calculate_ctr(), "%")
