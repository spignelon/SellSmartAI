import logging
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TAEMExtractor:
    """
    A Text-Attribute Extraction Model (TAEM) conceptual implementation
    built on transformer architectures for identifying and extracting
    product details from unstructured text.

    This example uses a pre-trained Named Entity Recognition (NER) model.
    For optimal performance on specific e-commerce attributes, this model
    should be fine-tuned on a custom dataset of product descriptions
    annotated with the desired attributes (e.g., BRAND, PRODUCT_NAME, PRICE, etc.).
    """

    def __init__(self, model_name_or_path="dslim/bert-base-NER"):
        """
        Initializes the TAEMExtractor with a pre-trained transformer model.

        Args:
            model_name_or_path (str): The name of the pre-trained model from
                                      Hugging Face Model Hub or path to a local model.
                                      "dslim/bert-base-NER" is a general NER model.
                                      Replace with your fine-tuned model for e-commerce.
        """
        try:
            logger.info(f"Loading NER model and tokenizer: {model_name_or_path}...")
            # Using AutoModelForTokenClassification and AutoTokenizer for flexibility
            self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
            self.model = AutoModelForTokenClassification.from_pretrained(model_name_or_path)
            
            # Using the Hugging Face pipeline for NER, which handles
            # tokenization, prediction, and aggregation of entities.
            # We specify `ignore_labels=[]` if we want to see all predicted entities,
            # or list labels to ignore if needed.
            # `grouped_entities=True` (older versions) or `aggregation_strategy="simple"` (newer versions)
            # helps in merging sub-word tokens into single entities.
            # The pipeline handles this internally.
            # For newer versions, aggregation_strategy might be needed.
            # Trying with a more compatible approach for various versions
            self.ner_pipeline = pipeline(
                "ner",
                model=self.model,
                tokenizer=self.tokenizer,
                # grouped_entities=True # Deprecated in some versions
                # aggregation_strategy="simple" # Use if available and preferred
            )
            logger.info("NER model and tokenizer loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading NER model: {e}")
            logger.error(
                "Please ensure you have a working internet connection to download the model "
                "or that the model path is correct."
            )
            logger.error(
                "For a custom TAEM, you would typically fine-tune a transformer model "
                "on e-commerce specific attributes."
            )
            self.ner_pipeline = None

    def extract_attributes(self, text):
        """
        Extracts attributes from the given unstructured text.

        Args:
            text (str): The unstructured text string (e.g., product description,
                        social media post).

        Returns:
            list: A list of dictionaries, where each dictionary represents an
                  extracted entity (attribute) with its type, word, score,
                  start, and end character index.
                  Example: [{'entity_group': 'BRAND', 'word': 'Apple', ...}]
                  Returns an empty list if the pipeline is not initialized or an error occurs.
        """
        if not self.ner_pipeline:
            logger.error("NER pipeline not initialized. Cannot extract attributes.")
            return []
        if not text or not isinstance(text, str):
            logger.warning("Input text is empty or not a string. Returning empty list.")
            return []

        try:
            logger.info(f"Extracting attributes from text: '{text[:100]}...'")
            # The pipeline returns a list of entities.
            # Each entity is a dict with keys like 'entity' (or 'entity_group'), 'score', 'word', 'start', 'end'.
            # The exact key for the entity type might vary ('entity' or 'entity_group')
            # depending on the transformers version and model.
            raw_entities = self.ner_pipeline(text)
            
            # Standardize the output key for entity type to 'entity_group'
            processed_entities = []
            for entity in raw_entities:
                entity_type_key = 'entity_group' if 'entity_group' in entity else 'entity'
                processed_entity = {
                    'entity_group': entity[entity_type_key],
                    'word': entity['word'],
                    'score': round(entity['score'], 4), # score is float32, convert for easier use
                    'start': entity['start'],
                    'end': entity['end']
                }
                processed_entities.append(processed_entity)
            
            logger.info(f"Successfully extracted {len(processed_entities)} attributes.")
            return processed_entities
        except Exception as e:
            logger.error(f"Error during attribute extraction: {e}")
            return []

    def display_attributes(self, text, attributes):
        """
        Displays the extracted attributes in a user-friendly format.

        Args:
            text (str): The original text.
            attributes (list): The list of extracted attributes from extract_attributes.
        """
        print(f"\n--- Attributes for text: '{text}' ---")
        if attributes:
            for attr in attributes:
                # The 'word' from the pipeline might sometimes have special characters (like ## for subwords if not aggregated)
                # or might be a cleaned version.
                # Using start/end indices is more robust to reconstruct if needed, though 'word' is usually what's desired.
                print(
                    f"  - Type: {attr['entity_group']}, "
                    f"Value: '{attr['word']}' (Confidence: {attr['score']:.2f}) "
                    f"[Pos: {attr['start']}-{attr['end']}]"
                )
        else:
            print("  No attributes extracted or an error occurred.")
        print("----------------------------------------")

# --- Example Usage ---
if __name__ == "__main__":
    # --- Simple Example using a generic NER model ---
    # Note: "dslim/bert-base-NER" recognizes PER (Person), ORG (Organization), LOC (Location), MISC.
    # It will NOT recognize e-commerce specific attributes like BRAND, PRICE, etc.,
    # unless you fine-tune it or use a model specifically fine-tuned for such tasks.
    
    print("--- TAEM Extractor: Generic NER Example ---")
    # Initialize with the default generic NER model
    generic_extractor = TAEMExtractor()

    example_text_1 = (
        "Ujjawal Saini from New Delhi visited the Apple Store in California. "
        "He bought an iPhone 15 Pro for $999."
    )
    
    if generic_extractor.ner_pipeline: # Check if pipeline initialized successfully
        attributes_1 = generic_extractor.extract_attributes(example_text_1)
        generic_extractor.display_attributes(example_text_1, attributes_1)

    example_text_2 = (
        "The new SellSmart AI project by Google at the East Delhi Campus "
        "aims to revolutionize e-commerce."
    )
    if generic_extractor.ner_pipeline:
        attributes_2 = generic_extractor.extract_attributes(example_text_2)
        generic_extractor.display_attributes(example_text_2, attributes_2)

    # --- Conceptual Example for E-commerce (if you had a fine-tuned model) ---
    print("\n--- TAEM Extractor: Conceptual E-commerce Example ---")
    print(
        "INFO: The following example assumes you have a model fine-tuned for e-commerce attributes "
        "like 'BRAND', 'PRODUCT', 'PRICE'."
    )
    print("INFO: We will still use 'dslim/bert-base-NER' here, so it won't identify these specific tags.")
    
    # If you had a custom fine-tuned model for e-commerce attributes, you would load it like this:
    # ecommerce_model_path = "path/to/your/fine_tuned_ecommerce_ner_model"
    # ecommerce_extractor = TAEMExtractor(model_name_or_path=ecommerce_model_path)
    # For demonstration, we'll reuse the generic_extractor:
    ecommerce_extractor = generic_extractor 

    ecommerce_text = (
        "Check out this amazing Sony WH-1000XM4 noise-cancelling headphones, "
        "now only $278! Made from premium materials."
    )
    
    if ecommerce_extractor.ner_pipeline:
        # With dslim/bert-base-NER, 'Sony' might be tagged as ORG.
        # A fine-tuned model would ideally tag 'Sony' as BRAND, 'WH-1000XM4' as PRODUCT, '$278' as PRICE.
        ecommerce_attributes = ecommerce_extractor.extract_attributes(ecommerce_text)
        ecommerce_extractor.display_attributes(ecommerce_text, ecommerce_attributes)
        
        print("\nReminder: To get specific e-commerce attributes like BRAND, PRODUCT_NAME, PRICE, MATERIAL, etc.,")
        print("you need to fine-tune a transformer model on a dataset annotated with these entities.")
        print("The 'dslim/bert-base-NER' model used here is for general entities (Person, Organization, Location).")