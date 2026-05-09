import streamlit as st
import requests
import os
from dotenv import load_dotenv
from fpdf import FPDF
from PyPDF2 import PdfReader

load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not WEATHER_API_KEY:
    st.error("Make sure WEATHER_API_KEY exists in the .env file")
    st.stop()

st.set_page_config(page_title="Weather Viewer & PDF QA")
st.title("Smart Weather Viewer & PDF Question Answering")

st.header("Weather Data")
city = st.text_input("Enter city name (e.g., Ismailia):")

def get_weather(city):
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}"
        res = requests.get(url).json()
        
        if "error" in res:
            return None, f"City '{city}' not found or API error."
            
        data = {
            "city": res["location"]["name"],
            "temperature": res["current"]["temp_c"],
            "humidity": res["current"]["humidity"],
            "wind_speed": round(res["current"]["wind_kph"] / 3.6, 2),
            "description": res["current"]["condition"]["text"]
        }
        return data, None
    except Exception as e:
        return None, f"Connection error: {str(e)}"

def create_pdf(weather_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Weather Report for {weather_data['city']}", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Temperature: {weather_data['temperature']} C", ln=True)
    pdf.cell(0, 10, f"Humidity: {weather_data['humidity']}%", ln=True)
    pdf.cell(0, 10, f"Wind Speed: {weather_data['wind_speed']} m/s", ln=True)
    pdf.cell(0, 10, f"Description: {weather_data['description']}", ln=True)
    return pdf.output(dest='S').encode('latin1')

if city:
    with st.spinner("Fetching weather data..."):
        weather, error = get_weather(city)

    if error:
        st.error(error)
    else:
        st.success(f"Weather data for {weather['city']}:")
        st.markdown(f"- Temperature: {weather['temperature']} C")
        st.markdown(f"- Humidity: {weather['humidity']}%")
        st.markdown(f"- Wind Speed: {weather['wind_speed']} m/s")
        st.markdown(f"- Description: {weather['description']}")

        pdf_bytes = create_pdf(weather)
        st.download_button(
            label="Download Weather PDF",
            data=pdf_bytes,
            file_name=f"{weather['city']}_weather_report.pdf",
            mime="application/pdf"
        )

st.header("Ask Questions from Your PDF")

pdf_file = st.file_uploader("Upload your PDF", type="pdf", key="pdf_qa")

if pdf_file:
    reader = PdfReader(pdf_file)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    st.text_area("Preview of PDF content", full_text[:1000] + "...", height=200)

    question = st.text_input("Enter your question about the PDF content:", key="pdf_question")

    if question:
        st.write("Searching for answer...")
        if question.lower() in full_text.lower():
            st.success("Your question matches content in the PDF.")
        else:
            st.info("Your question was not found in the PDF.")
