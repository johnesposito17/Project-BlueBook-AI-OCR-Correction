from openai import OpenAI

# OCR Correction using OpenAI inputting one form at a time
# Inefficient for doing documents in bulk
# proof of concept
# potential expirimentaion with prompt and temparture settings needed


# Initialize client with your API key
client = OpenAI(api_key="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")

def OCR_correction(input_string):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """This text is from reports of UFO (or UAP) sightings from the period 1947-1969. It was created using optical character recognition (OCR) software and it contains OCR errors, especially when the original document was illegible or redacted. Some of the pages are formatted as memorandums while others contain forms. The form fields titles and data are sometimes mixed up due to the layout of the form. There are two types of forms, one is formatted as follows.

PROJECT (number) RECORD 
1. DATE - TIME GROUP: 
2. LOCATION: 
3. SOURCE: 
4. NUMBER OF OBJECTS: 
5. LENGTH OF OBSERVATION: 
6. TYPE OF OBSERVATION: 
7. COURSE: 
8. PHOTOS:  (Yes or No checkboxes with selection marked with X)
9. PHYSICAL EVIDENCE: (Yes or No checkboxes with selection marked with X)
10. CONCLUSION: 
11. BRIEF SUMMARY AND ANALYSIS: 
FORM (alphanumeric code) Previous editions of this form may be used.

The second type of form is formatted like this:

Check-List - UNIDENTIFIED FLYING OBJECTS 
Incident #
1. Date 
2. Time
3. Location
4. Name of observer 
5. Occupation of observer
6. Address of observer 
7. Place of observation
8. Number of objects
9. Distance of object
10. Time in sight
11. Altitude
12. Speed
13. Direction of flight
14. Tactics
15. Sound
16. Size
17. Color
18. Shape
19. Odor
20. Apparent construction
21. Exhaust trails
22. Weather conditions
23. Effect on clouds
24. Sketches or photographs
25. Manner of disappearance
26. Remarks 

Fix all OCR errors in the user’s text, even if they are subtle. Always return a corrected version. Do not include any extra commentary—just the cleaned-up text."""
                },
                {
                    "role": "user",
                    "content": input_string
                }
            ],
            temperature=0.0,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    input_text = """
NATlONAL ARCHlVES MlCROFlLM PUBLlCATlONS
MlCROFlLM Publcatlon T1206
PROJCT BLUE BOK
RoII I
Case F1les of lndlvldual Slghtlngs
lndex
and
FIle Nos. . 1-54
Summer 1947-JuIy 9, 1947
OF
LlTTER
SCRlPTA
The
the
*
1934
THE NATlONAL ARCHlVES
NATlONAL ARCHlVES AND RECORDS SERVlCE
GENERAL SERVlCES ADMINlSTRATlON
WASHlNGTON: 1976
"""

    print(OCR_correction(input_text))


    print(OCR_correction("""
AUGUST THROUGH 1947 SIGHTINGS
INCIDENT
NUMBER
DATE
LOCATION
OBSERVER
EVALUATION
AUGUST
71
Aug
Milan, Italy (CASE MISSING) Civilian PHOTO Insuffici ent Data
12
DR Aug
Danforth, Illinois
Farmer 0.) Other (Hoax)
73
88
3 Aug
Hackensack, New Jersey
Insufficient Data
74
4
Boston, Massachusetts
Astro (Sun Dog)
75
a
58
4
Bethel, Alask
A/C
06
69,70
6
Philadelphia, Pennsylvania
Multiple
Astro (Neteor)
-
n
66
10
Silver Springs, Ohio
Astro (Meteor)
79
76
13
Salmon Dam, Idaho
A/C
80
75
13
Twin Falls, Idaho
Other (Atmospheric Ed
81
67
14
S. Placerville, California
Astro (Meteor) -
82
135
15-20
Weaver, South Dakota
AF Officer
UNIDENTE: ISD Birds
83
64
19
Twin Falls, Idaho
Other (Birds) -
84
Late Aug
Holloman AFB, New Mexico
(RADAR)
Other (False Targets)
78
NONE
11 Aug
St. Louis, Missouri
None
SEPTEMBER
85
51
3
Oswego, Oregon
UNIDENTI FIED -
-
86
61, 52
to
Logan, Utah
Other (Birds)
87
59
12
Pacific Ocean (Necker I.)
Military Air
Astro
88
72
17
Ft Richardson, Alaska
Arnty Officer
Astro (feteor)
-
89
18
20
Toronto, Canada
Not Stated
Other (Hoax)
OCTOBER
90 179
Oct
Son Francisco, California Not Stated
Insufficient Data-
91
Oct
Dodgeville,
UMIDENTIFI: DD -
92 71
8 or 9
Las Vegas, Nevada
Other (Contrails) AK
93
12
Mexico
Multi
Astro (Meteor) -
94 34
13
Dauphin, Minnesota
Multiple
Astro (Met eor)
95 37
14
Phoenix, Arizona
96 19
20
Deyton, Ohio
A/C
-
91 20
20
Xenia, Ohio
A/C -
NOVEMBER
98 36
Nov
Boise, Idaho
CAA Observer
Insufficient Data:
99 98
2
Houston, Texas
Astro (teteor)
100 35
12
Cape Blanco, Oregon
Astro (feteor)
101 289
12
La Junta &: Pueblo, Colorado (CASE MISSING)
Insufficient Data
102 225
""Late 1947
Vaughn, New Medico
Other (Flares)
103
december
23 DE Dulka,
104
132
12
Oslo, Norway
Astro eteor)
1/05
31
Mid Dec
Northern Arizona
Other (Contrail)
100 99,95,97 30
Oregon, Nevada, Califomia
Hultiple
Astro (Neteor)
109
Dec 1947- Jen 1948 Wildwood New Jersey
Other (Mirage)
108
act 07 Nov 1947 Philadelphea,Pa"""))