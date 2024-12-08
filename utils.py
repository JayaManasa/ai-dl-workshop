from pdf2image import convert_from_bytes
from io import BytesIO
import tempfile
from PIL import Image
import google.generativeai as genai


# Configure the Gemini API (you'll need to set up your API key)
genai.configure(api_key='o')
model = genai.GenerativeModel('gemini-1.5-flash')

# Helper function to convert PDF content into images
def convert_pdf_to_images(pdf_content):
    # Use a temporary file to store the PDF content
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(pdf_content)
        temp_pdf.flush()  # Ensure all data is written to the file
        images = convert_from_bytes(pdf_content)

    image_bytes_list = []
    for image in images:
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        image_bytes_list.append(img_byte_arr.getvalue())

    return image_bytes_list


# Placeholder function to process images with Gemini
def process_images_with_gemini(images):
    # TODO: Implement actual Gemini API call
    prompt = """ 
    Analyze these grocery bill invoices. For each edible product listed, provide a comprehensive nutritional and environmental assessment based on the estimated quantity purchased. Use the following format for each product:

    {
        "product_name": "",
        "price_paid": 0,
        "num_items": 0,
        "estimated_quantity": {"value": 0, "unit": ""},
        "serving_size": "",
        "energy": {
            "per_serving": {"value": 0, "unit": "kcal"}
        },
        "macronutrients": {
            "total_fat": {"per_serving": {"value": 0, "unit": "g"}},
            "carbohydrates": {"per_serving": {"value": 0, "unit": "g"}},
            "protein": {"per_serving": {"value": 0, "unit": "g"}}
        },
        "micronutrients": {
            "sodium": {"per_serving": {"value": 0, "unit": "mg"}},
            "key_vitamins_minerals": [
                {"name": "", "value": 0, "unit": ""}
            ]
        },
        "fiber": {
            "total": {"per_serving": {"value": 0, "unit": "g"}},
            "soluble": {"per_serving": {"value": 0, "unit": "g"}},
            "insoluble": {"per_serving": {"value": 0, "unit": "g"}}
        },
        "allergens": [],
        "nutrient_density_score": 0,
        "glycemic_index": 0,
        "glycemic_load": 0,
        "protein_quality": {
            "score": 0,
            "method": "PDCAAS/DIAAS"
        },
        "phytonutrients": [
            {"name": "", "presence": "high/medium/low"}
        ],
        "micronutrient_density": {
            "per_100_calories": [
                {"nutrient": "", "value": 0, "unit": ""}
            ],
            "per_100_grams": [
                {"nutrient": "", "value": 0, "unit": ""}
            ]
        },
        "satiety_index": 0,
        "environmental_impact": {
            "water_usage": {"value": 0, "unit": "L/kg"},
            "carbon_footprint": {"value": 0, "unit": "kg CO2e/kg"},
            "land_use": {"value": 0, "unit": "m²/kg"}
        },
        "versatility_score": 0,
        "cost_nutrient_ratio": 0,
        "nutritional_summary": ""
    }

    Estimate the quantity based on the price paid and typical market prices. Provide rough estimates for nutritional content and environmental impact based on this estimated quantity. If certain information is not applicable or available, you may omit those fields. Focus on providing a general nutritional and environmental overview rather than precise values.

    For each metric:
    1. Nutrient Density Score: Calculate based on vitamin, mineral, fiber, and protein content relative to calorie content.
    2. Glycemic Index and Load: Assess these values, noting that foods like lentils and pulses typically have low values.
    3. Protein Quality: Evaluate using PDCAAS or DIAAS metrics where possible.
    4. Fiber Content: Analyze both quantity and type (soluble vs. insoluble).
    5. Phytonutrient Profile: Assess the presence of beneficial compounds like polyphenols, flavonoids, and antioxidants.
    6. Micronutrient Density: Compare vitamin and mineral content per 100 calories and per 100 grams.
    7. Satiety Index: Provide an estimate of how filling the food is relative to its calorie content.
    8. Environmental Impact: Include metrics on water usage, carbon footprint, and land use for production.
    9. Versatility Score: Develop a score based on the food's adaptability to various dishes and cuisines.
    10. Cost-Nutrient Ratio: Calculate the nutritional value provided per unit of cost.

    List all edible products from the invoices in this format, highlighting the nutritional benefits of foods like lentils, pulses, and other nutrient-dense options.
    """

    all_results = []
    for img_bytes in images:
        # Convert bytes to PIL Image
        image = Image.open(BytesIO(img_bytes))

        # Generate content with Gemini
        response = model.generate_content([prompt, image])

        # Append the response to results
        all_results.append(response.text)

    # Combine all results
    combined_result = "\n\n".join(all_results)

    return combined_result
    return f"Processed {len(images)} images with Gemini"




