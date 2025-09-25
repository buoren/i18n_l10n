"""
Example usage of the translation system
"""

from .database import db_manager, LanguageCode

def example_translation_usage():
    """Example of how to use the translation system"""
    
    # Create a translation tag with context
    app_name = "i18n-l10n-app"
    tag_text = "Hello World"
    context = "Main greeting message displayed on the homepage"
    tag_id = db_manager.create_translation_tag(app_name, tag_text, context)
    
    if tag_id:
        print(f"Created translation tag with ID: {tag_id}")
        
        # Add translations for different languages
        translations = [
            (LanguageCode.EN_US, "Hello World"),
            (LanguageCode.ES_ES, "Hola Mundo"),
            (LanguageCode.FR_FR, "Bonjour le Monde"),
            (LanguageCode.DE_DE, "Hallo Welt"),
            (LanguageCode.IT_IT, "Ciao Mondo"),
            (LanguageCode.PT_BR, "Olá Mundo"),
            (LanguageCode.RU_RU, "Привет, мир"),
            (LanguageCode.JA_JP, "こんにちは世界"),
            (LanguageCode.KO_KR, "안녕하세요 세계"),
            (LanguageCode.ZH_CN, "你好世界"),
            (LanguageCode.AR_SA, "مرحبا بالعالم"),
        ]
        
        # Save translations
        for language, text in translations:
            success = db_manager.save_translation(
                translation_tag_id=tag_id,
                language=language,
                text=text
            )
            if success:
                print(f"✓ Saved {language.value}: {text}")
            else:
                print(f"✗ Failed to save {language.value}")
        
        # Retrieve translations
        print("\n--- Retrieving translations ---")
        all_translations = db_manager.get_translations_for_tag(tag_id)
        for lang_code, text in all_translations.items():
            print(f"{lang_code}: {text}")
        
        # Get specific translation
        print(f"\nEnglish translation: {db_manager.get_translation(tag_id, LanguageCode.EN_US)}")
        print(f"Spanish translation: {db_manager.get_translation(tag_id, LanguageCode.ES_ES)}")
        
        # Get available languages
        available_langs = db_manager.get_available_languages()
        print(f"\nAvailable languages: {[lang.value for lang in available_langs]}")
    
    else:
        print("Failed to create translation tag")

if __name__ == "__main__":
    example_translation_usage()
