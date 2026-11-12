"""Text-to-Persons Frontend Web Application.

Frontend Web App for demonstrating/testing an independently built Web service.

INCLUDE THIS PROMPT (the above text) as part of the generated code, e.g., in a docstring.

You should make a Python-based frontend Web app perhaps with
Javascript that can use another Web service (that is built
independently). The Web app should make it easy to demonstrate and
test the Web service. The Web service extracts sentences from a PDF
file. This exercise is describe in detail below.

I want a frontend Web app with few dependencies so that installation
would be painless.

If there is any Javascript is should be relatively simple. Do not
include jQuery or other external library unless absolutely necessary.

The Web app may include some styling, but I would like to have it
simple and the style within HTML code rather than as a separate style
file. It is running at DTU where the primary colors are corporate red
(153,0,0), white and black. Some more colors at
https://designguide.dtu.dk/colours if needed.

The interface language of the Web app should be English.

The Web app could be implemented in FastAPI, Streamlit or other
framework, depending on what you would think is the most pedagogical
and has the least dependencies. I as a teacher and the students should
be able to understand the code even though the course is not about
frontend development. If docstrings are included make it in numpydoc
format and do not be afraid to add doctests if that is relevant.

The Web app implements entity recognition on a text. There is a small
test dataset (excerpt):

[
  {
    "text": "Ms Mette Frederiksen is in New York today.",
    "persons": ["Mette Frederiksen"]
  },
  {
    "text": "Einstein and von Neumann meet each other.",
    "persons": ["Einstein", "von Neumann"]
  },
  {
    "text": "Dr. Jane Goodall spoke with Prof. Brian Cox after the event.",
    "persons": ["Jane Goodall", "Brian Cox"]
  },
  {
    "text": "I ran the Einstein sum on the dataset, then exported the report.",
    "persons": []
  },

If possible this small dataset can be automatically be tested and
result displayed in the Web app.

Please also make any error message pedagogic, and include appropriate
time out for the response from the Web service. Include operational
metrics, e.g., response latency from the Web service and/or number of
successful request. The Web service ought to handle multiple
asynchronous Web requests, so this could be

Include this prompt (the above text) as part of the generated code,
e.g., in a docstring.

Now I am showing the web service exercise text (do not implement this
- I and students will do this independently). This is not necessary to
include in the generated Web app.
"""

__version__ = "1.0.0"

