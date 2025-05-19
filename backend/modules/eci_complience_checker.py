import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple

# --- Data Structures ---

@dataclass
class ProductListing:
    """
    Represents the data of a product listing to be checked.
    """
    product_id: str
    title: str
    description: str
    images: List[str]  # List of image URLs or identifiers
    price: float
    category: str
    attributes: Dict[str, Any] = field(default_factory=dict)  # e.g., {"brand": "XYZ", "color": "Red"}
    keywords: List[str] = field(default_factory=list) # Keywords targeted for SEO

@dataclass
class ComplianceIssue:
    """
    Represents a single compliance or SEO issue found.
    """
    rule_id: str
    message: str
    severity: str  # e.g., "CRITICAL", "WARNING", "INFO", "SEO_SUGGESTION"
    details: Optional[Dict[str, Any]] = None

# --- Rule Definition ---

class ComplianceRule(ABC):
    """
    Abstract base class for all compliance and SEO rules.
    """
    def __init__(self, rule_id: str, description: str, severity: str = "WARNING", weight: float = 1.0):
        self.rule_id = rule_id
        self.description = description
        self.severity = severity
        self.weight = weight # Used for scoring

    @abstractmethod
    def evaluate(self, listing: ProductListing) -> Optional[ComplianceIssue]:
        """
        Evaluates the product listing against this rule.

        Returns:
            ComplianceIssue object if the rule is violated, None otherwise.
        """
        pass

# --- Concrete Rule Implementations (Examples) ---

# --- Title Rules ---
class TitleLengthRule(ComplianceRule):
    def __init__(self, rule_id: str, min_length: int, max_length: int, severity: str = "CRITICAL", weight: float = 10.0):
        super().__init__(rule_id, f"Title length must be between {min_length} and {max_length} characters.", severity, weight)
        self.min_length = min_length
        self.max_length = max_length

    def evaluate(self, listing: ProductListing) -> Optional[ComplianceIssue]:
        title_len = len(listing.title)
        if not (self.min_length <= title_len <= self.max_length):
            return ComplianceIssue(
                self.rule_id,
                f"Title length is {title_len}. Expected between {self.min_length} and {self.max_length}.",
                self.severity,
                details={"current_length": title_len, "min": self.min_length, "max": self.max_length}
            )
        return None

class TitleCapitalizationRule(ComplianceRule):
    def __init__(self, rule_id: str, severity: str = "WARNING", weight: float = 2.0):
        super().__init__(rule_id, "Title should use title case (first letter of each major word capitalized).", severity, weight)

    def evaluate(self, listing: ProductListing) -> Optional[ComplianceIssue]:
        # This is a simplistic check. Real title case is more complex.
        if not listing.title == listing.title.title() and not listing.title.isupper():
             # Allow all caps titles for some brands/styles, but flag mixed non-title case.
            is_mostly_title_case = sum(1 for word in listing.title.split() if word[0].isupper()) / len(listing.title.split()) > 0.7
            if not is_mostly_title_case and len(listing.title.split()) > 1 : # Avoid flagging single-word all-lower titles
                return ComplianceIssue(
                    self.rule_id,
                    "Title does not appear to be in title case. Please review capitalization.",
                    self.severity
                )
        return None

class TitleForbiddenWordsRule(ComplianceRule):
    def __init__(self, rule_id: str, forbidden_words: List[str], severity: str = "CRITICAL", weight: float = 5.0):
        super().__init__(rule_id, f"Title contains forbidden words: {', '.join(forbidden_words)}.", severity, weight)
        self.forbidden_words_lower = [word.lower() for word in forbidden_words]

    def evaluate(self, listing: ProductListing) -> Optional[ComplianceIssue]:
        found_words = [word for word in self.forbidden_words_lower if re.search(r'\b' + re.escape(word) + r'\b', listing.title.lower())]
        if found_words:
            return ComplianceIssue(
                self.rule_id,
                f"Title contains forbidden words: {', '.join(found_words)}.",
                self.severity,
                details={"found_words": found_words}
            )
        return None

# --- Description Rules ---
class DescriptionLengthRule(ComplianceRule):
    def __init__(self, rule_id: str, min_length: int, severity: str = "WARNING", weight: float = 5.0):
        super().__init__(rule_id, f"Description should be at least {min_length} characters long.", severity, weight)
        self.min_length = min_length

    def evaluate(self, listing: ProductListing) -> Optional[ComplianceIssue]:
        if len(listing.description) < self.min_length:
            return ComplianceIssue(
                self.rule_id,
                f"Description length is {len(listing.description)}. Expected at least {self.min_length}.",
                self.severity,
                details={"current_length": len(listing.description), "min": self.min_length}
            )
        return None

class DescriptionHtmlCheckRule(ComplianceRule):
    def __init__(self, rule_id: str, allow_html: bool = False, severity: str = "CRITICAL", weight: float = 3.0):
        super().__init__(rule_id, "HTML content in description check.", severity, weight)
        self.allow_html = allow_html

    def evaluate(self, listing: ProductListing) -> Optional[ComplianceIssue]:
        has_html = bool(re.search(r'<[^>]+>', listing.description))
        if not self.allow_html and has_html:
            return ComplianceIssue(
                self.rule_id,
                "HTML tags are not allowed in the description for this marketplace.",
                self.severity
            )
        return None

# --- Image Rules ---
class ImageCountRule(ComplianceRule):
    def __init__(self, rule_id: str, min_images: int, max_images: int, severity: str = "CRITICAL", weight: float = 8.0):
        super().__init__(rule_id, f"Number of images must be between {min_images} and {max_images}.", severity, weight)
        self.min_images = min_images
        self.max_images = max_images

    def evaluate(self, listing: ProductListing) -> Optional[ComplianceIssue]:
        image_count = len(listing.images)
        if not (self.min_images <= image_count <= self.max_images):
            return ComplianceIssue(
                self.rule_id,
                f"Number of images is {image_count}. Expected between {self.min_images} and {self.max_images}.",
                self.severity,
                details={"current_count": image_count, "min": self.min_images, "max": self.max_images}
            )
        return None

# --- Attribute Rules ---
class RequiredAttributeRule(ComplianceRule):
    def __init__(self, rule_id: str, attribute_name: str, severity: str = "CRITICAL", weight: float = 7.0):
        super().__init__(rule_id, f"Attribute '{attribute_name}' is required.", severity, weight)
        self.attribute_name = attribute_name

    def evaluate(self, listing: ProductListing) -> Optional[ComplianceIssue]:
        if self.attribute_name not in listing.attributes or not listing.attributes[self.attribute_name]:
            return ComplianceIssue(
                self.rule_id,
                f"Required attribute '{self.attribute_name}' is missing or empty.",
                self.severity,
                details={"attribute_name": self.attribute_name}
            )
        return None

# --- SEO Rules (Examples) ---
class KeywordInTitleRule(ComplianceRule):
    def __init__(self, rule_id: str, severity: str = "SEO_SUGGESTION", weight: float = 3.0):
        super().__init__(rule_id, "Primary keywords should be present in the title.", severity, weight)

    def evaluate(self, listing: ProductListing) -> Optional[ComplianceIssue]:
        if not listing.keywords:
            return None # No keywords to check against
        
        missing_keywords = [kw for kw in listing.keywords if kw.lower() not in listing.title.lower()]
        if len(missing_keywords) == len(listing.keywords) and listing.keywords: # If all primary keywords are missing
            return ComplianceIssue(
                self.rule_id,
                f"Consider adding primary keywords ({', '.join(listing.keywords)}) to the title for better SEO.",
                self.severity,
                details={"missing_keywords": listing.keywords}
            )
        elif missing_keywords:
             return ComplianceIssue(
                self.rule_id,
                f"Consider adding keywords like '{', '.join(missing_keywords)}' to the title for better SEO.",
                self.severity,
                details={"missing_keywords": missing_keywords}
            )
        return None

class KeywordInDescriptionRule(ComplianceRule):
    def __init__(self, rule_id: str, min_occurrences: int = 1, severity: str = "SEO_SUGGESTION", weight: float = 2.0):
        super().__init__(rule_id, f"Primary keywords should appear at least {min_occurrences} time(s) in the description.", severity, weight)
        self.min_occurrences = min_occurrences

    def evaluate(self, listing: ProductListing) -> Optional[ComplianceIssue]:
        if not listing.keywords:
            return None

        for keyword in listing.keywords:
            # Simple count, could be improved with regex for whole words
            if listing.description.lower().count(keyword.lower()) < self.min_occurrences:
                return ComplianceIssue(
                    self.rule_id,
                    f"Keyword '{keyword}' appears less than {self.min_occurrences} time(s) in the description. Consider adding it more for SEO.",
                    self.severity,
                    details={"keyword": keyword, "current_occurrences": listing.description.lower().count(keyword.lower())}
                )
        return None

# --- Marketplace Profile ---

@dataclass
class MarketplaceProfile:
    """
    Defines a set of compliance and SEO rules for a specific marketplace.
    """
    marketplace_name: str
    rules: List[ComplianceRule] = field(default_factory=list)

    def add_rule(self, rule: ComplianceRule):
        self.rules.append(rule)

# --- ECI Checker ---

@dataclass
class ComplianceReport:
    """
    Contains the results of a compliance check.
    """
    listing_id: str
    marketplace_name: str
    compliance_score: float  # Score from 0.0 to 100.0
    issues: List[ComplianceIssue] = field(default_factory=list)
    is_compliant: bool = True # Overall compliance status based on critical issues

    def __str__(self):
        report_str = f"--- Compliance Report for Listing '{self.listing_id}' on '{self.marketplace_name}' ---\n"
        report_str += f"Compliance Score: {self.compliance_score:.2f}%\n"
        report_str += f"Overall Compliant: {'Yes' if self.is_compliant else 'No (Critical Issues Found)'}\n"
        if self.issues:
            report_str += "Issues Found:\n"
            for issue in self.issues:
                report_str += f"  - [{issue.severity}] Rule ID: {issue.rule_id}: {issue.message}\n"
                if issue.details:
                    report_str += f"    Details: {issue.details}\n"
        else:
            report_str += "No issues found. Excellent!\n"
        report_str += "-------------------------------------------------------------\n"
        return report_str


class ECIChecker:
    """
    Performs compliance and SEO checks on a product listing against a marketplace profile.
    """
    def __init__(self, marketplace_profile: MarketplaceProfile):
        self.marketplace_profile = marketplace_profile

    def check_listing_compliance(self, listing: ProductListing) -> ComplianceReport:
        """
        Checks the given product listing against all rules in the marketplace profile.

        Returns:
            A ComplianceReport object with the score and list of issues.
        """
        issues_found: List[ComplianceIssue] = []
        total_possible_weight = 0
        achieved_weight = 0
        has_critical_issues = False

        for rule in self.marketplace_profile.rules:
            total_possible_weight += rule.weight
            issue = rule.evaluate(listing)
            if issue:
                issues_found.append(issue)
                if issue.severity == "CRITICAL":
                    has_critical_issues = True
                # For scoring, we only add weight if the rule is passed (no issue)
            else:
                achieved_weight += rule.weight
        
        compliance_score = (achieved_weight / total_possible_weight) * 100 if total_possible_weight > 0 else 100.0
        
        # The report mentions specific scores like 68% to 97% or 6.2/10 to 9.5/10.
        # This scoring is a simple weighted sum. It can be adjusted.
        # For example, a 0-10 score could be compliance_score / 10.

        return ComplianceReport(
            listing_id=listing.product_id,
            marketplace_name=self.marketplace_profile.marketplace_name,
            compliance_score=compliance_score,
            issues=issues_found,
            is_compliant=not has_critical_issues
        )

# --- Example Usage ---
if __name__ == "__main__":
    # 1. Define a Product Listing
    sample_listing_1 = ProductListing(
        product_id="XYZ123",
        title="Awesome New Super FAST Gadget Pro X1000 Special Edition", # Potentially too long, "FAST" not title case
        description="This is a short description.", # Potentially too short
        images=["img1.jpg"], # Potentially too few
        price=199.99,
        category="Electronics",
        attributes={"brand": "GadgetBrand", "color": "Black"},
        keywords=["Super Gadget", "Pro X1000"]
    )

    sample_listing_2 = ProductListing(
        product_id="ABC789",
        title="Elegant Wooden Photo Frame (4x6 Inch)",
        description="Capture your precious memories with this beautifully crafted elegant wooden photo frame. "
                    "Perfect for 4x6 inch photographs. Made from high-quality sustainable wood. "
                    "Ideal gift for weddings, anniversaries, or birthdays. Add a touch of class to your home decor. "
                    "This wooden photo frame is a top seller.",
        images=["frame_main.jpg", "frame_angle.jpg", "frame_lifestyle.jpg"],
        price=25.00,
        category="Home Decor",
        attributes={"brand": "DecorCo", "material": "Wood", "size": "4x6 Inch"},
        keywords=["wooden photo frame", "4x6 frame", "home decor"]
    )

    # 2. Create Marketplace Profiles with Rules

    # Amazon Profile
    amazon_profile = MarketplaceProfile(marketplace_name="Amazon")
    amazon_profile.add_rule(TitleLengthRule("AMZ_TITLE_LEN", min_length=10, max_length=70, weight=10))
    amazon_profile.add_rule(TitleCapitalizationRule("AMZ_TITLE_CASE", severity="INFO", weight=1))
    amazon_profile.add_rule(TitleForbiddenWordsRule("AMZ_TITLE_FORBIDDEN", forbidden_words=["FAST", "Special Edition"], weight=5))
    amazon_profile.add_rule(DescriptionLengthRule("AMZ_DESC_LEN", min_length=100, weight=8))
    amazon_profile.add_rule(DescriptionHtmlCheckRule("AMZ_DESC_HTML", allow_html=False, weight=3))
    amazon_profile.add_rule(ImageCountRule("AMZ_IMG_COUNT", min_images=3, max_images=7, weight=10))
    amazon_profile.add_rule(RequiredAttributeRule("AMZ_ATTR_BRAND", attribute_name="brand", weight=7))
    amazon_profile.add_rule(RequiredAttributeRule("AMZ_ATTR_COLOR", attribute_name="color", severity="WARNING", weight=3))
    amazon_profile.add_rule(KeywordInTitleRule("AMZ_SEO_KEY_TITLE", weight=5))
    amazon_profile.add_rule(KeywordInDescriptionRule("AMZ_SEO_KEY_DESC", min_occurrences=2, weight=3))

    # Flipkart Profile (example with slightly different rules)
    flipkart_profile = MarketplaceProfile(marketplace_name="Flipkart")
    flipkart_profile.add_rule(TitleLengthRule("FLP_TITLE_LEN", min_length=5, max_length=60, weight=10))
    flipkart_profile.add_rule(DescriptionLengthRule("FLP_DESC_LEN", min_length=50, weight=8))
    flipkart_profile.add_rule(ImageCountRule("FLP_IMG_COUNT", min_images=2, max_images=5, weight=10))
    flipkart_profile.add_rule(RequiredAttributeRule("FLP_ATTR_BRAND", attribute_name="brand", weight=7))
    flipkart_profile.add_rule(KeywordInTitleRule("FLP_SEO_KEY_TITLE", weight=5))


    # 3. Create ECI Checkers
    amazon_checker = ECIChecker(amazon_profile)
    flipkart_checker = ECIChecker(flipkart_profile)

    # 4. Perform Checks
    print("--- Checking Listing 1 (sample_listing_1) ---")
    amazon_report_1 = amazon_checker.check_listing_compliance(sample_listing_1)
    print(amazon_report_1)

    flipkart_report_1 = flipkart_checker.check_listing_compliance(sample_listing_1)
    print(flipkart_report_1)
    
    print("\n--- Checking Listing 2 (sample_listing_2) ---")
    amazon_report_2 = amazon_checker.check_listing_compliance(sample_listing_2)
    print(amazon_report_2)

    flipkart_report_2 = flipkart_checker.check_listing_compliance(sample_listing_2)
    print(flipkart_report_2)

    # Example of how to access specific details
    if not amazon_report_1.is_compliant:
        print(f"\nListing {sample_listing_1.product_id} has critical issues on Amazon:")
        for issue in amazon_report_1.issues:
            if issue.severity == "CRITICAL":
                print(f" - {issue.message}")

