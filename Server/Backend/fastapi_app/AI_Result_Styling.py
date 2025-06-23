import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configuring gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model=genai.GenerativeModel("gemini-1.5-flash")

def StyleResult(resume_text):
  prompt= f"""
{resume_text} is the result generated from the you from another function now our task is to beautify our result.
In the text there will be an overall score out of hundred so I want a unique way to represent it I want a beautiful voilet colour solid speedometer type icon appears whose min value is 0 and max value is 100 so whatever is the overall score the meter start from 0 and then go till the overall score now I want this icon to appear in the very beggining after that in next line in a the overall score appear in bold character.
Now we will show the result generated to user but since our box size is not too big so what we will do like if a sentence is very large then we will break into multiple lines so whatb youb have to to do is that if a sentence contains more than 10 words then understand it and break it into small sentences and show them into multiple lines.

Now I want you to use your intelligence to show the result generated in a beautiful manner so that when the user see it they get mesmerized if you want to use any icon with any word sentence or you want to use any beautiful font style or you want to bold important words you are allowed to do anything I just want you to create a beautiful result template so that if the user see it they get mesmerized.
 """
  
  response = model.generate_content([
    {
      "parts":[
        {"text": prompt}
      ]
    }
  ])

  return response.text

