from typing import List
from google.cloud import translate
client = translate.TranslationServiceClient()
parent = f"projects/translator-467314/locations/global"

def translate_batch(
    texts: List[str],
    target_lang: str,
    *,
    project_id: str,
    location: str = "global",
    mime: str = "text/plain"
) -> List[str]:
    client = translate.TranslationServiceClient()
    parent = f"projects/{project_id}/locations/{location}"

    response = client.translate_text(
        parent=parent,
        contents=texts,
        target_language_code=target_lang,
        mime_type=mime,
    )
    return [t.translated_text for t in response.translations]