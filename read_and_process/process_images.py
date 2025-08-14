from langchain.schema import Document
from PIL import Image
import io
from transformers import BlipProcessor, BlipForConditionalGeneration, BartForConditionalGeneration, BartTokenizer
import fitz
from langchain.schema import Document

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
summarization_model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
summarization_tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")


def process_images(file_path:str):
    print(f"In process images {file_path}")
    doc = fitz.open(file_path)
    chunks=[]

    for page_num in range(len(doc)):
        page_content = doc.load_page(page_num)
        text_content = page_content.get_text()
        captions=[]

        images = list(page_content.get_images(full=True))
        if not images:
            # Handle text-only page
            combined = f"Page content is {text_content}\n\nVisual content is None"
            inputs = summarization_tokenizer.encode(
                f"summarize: {combined} ", return_tensors="pt", max_length=1024, truncation=True
            )
            summ_ids = summarization_model.generate(
                inputs, max_length=150, min_length=50, length_penalty=2.0, num_beams=4, early_stopping=True
            )
            summary = summarization_tokenizer.decode(summ_ids[0], skip_special_tokens=True)
            print(summary)
            chunk = Document(
                page_content=summary,
                metadata={
                    "original_content": text_content,
                    "captions_generated": "No visual content"
                }
            )
            chunks.append(chunk)

        else:
            for idx, img in enumerate(images):
                print("Images detected, inside get_images")
                ref=img[0]
                img_bytes=doc.extract_image(ref)["image"]

                # print(f"Image dict {doc.extract_image(ref)}")

                try:
                    reassembled_image=Image.open(io.BytesIO(img_bytes))
                    print(f"The reassembled image")
                    inputs = processor(images=reassembled_image, return_tensors="pt")
                    output = model.generate(**inputs)
                    caption = processor.decode(output[0], skip_special_tokens=True)
                    print(f"Caption = {caption}")
                    captions.append(caption)
                except Exception as e:
                    print(f"Exception during image handling {e}")
                    caption="Issue with captioning"

                combined = f"""
                Page content is {text_content}\n\n
                Visual content is \n{caption}
                """

                inputs = summarization_tokenizer.encode(f"summarize: {combined} ", return_tensors="pt", max_length=1024, truncation=True)
                summ_ids = summarization_model.generate(inputs, max_length=150, min_length=50, length_penalty=2.0, num_beams=4, early_stopping=True)
                summary = summarization_tokenizer.decode(summ_ids[0], skip_special_tokens=True)
                print(summary)

                chunk = Document(
                    page_content=summary,
                    metadata={
                        "original_content":text_content,
                        "captions_generated":captions
                    }
                )

                chunks.append(chunk)   
        
    return chunks


