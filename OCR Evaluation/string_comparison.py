import re
import Levenshtein  # pip install python-Levenshtein

def clean_string(s: str) -> str:
    # Remove all ǂ...ǂ blocks (including delimiters)
    s = re.sub(r'ǂ.*?ǂ', '', s)

    # Replace ʘ...ʘ with just the inner content
    s = re.sub(r'ʘ(.*?)ʘ', r'\1', s)

    # Remove line breaks
    s = re.sub(r'[\r\n]+', ' ', s)

    # Collapse multiple spaces and strip
    s = re.sub(r'\s+', ' ', s).strip()

    return s


def distance(reference:str, hypothesis: str):
    ref_clean = clean_string(reference)
    hyp_clean = clean_string(hypothesis)
    if len(ref_clean) == 0:
        if len(hyp_clean) > 0:
            # Either return 1.0 (max CER), or a custom flag
            return 1.0
        else:
            return 0.0
    return Levenshtein.distance(ref_clean, hyp_clean)
    

def character_error_rate(reference: str, hypothesis: str) -> float:
    ref_clean = clean_string(reference)
    hyp_clean = clean_string(hypothesis)

    # if len(ref_clean) == 0:
    #     if len(hyp_clean) > 0:
    #         # Either return 1.0 (max CER), or a custom flag
    #         return 1.0
    #     else:
    #         return 0.0

    distance = Levenshtein.distance(ref_clean, hyp_clean)
    return distance / max(len(ref_clean), len(hyp_clean))


print(Levenshtein.distance("","""
                           the
                           
                           """))



ocr1 = """This case contains 2,
5% >
photos and 3,
negatives."""

human1 = """This case contains 2, 5” x 7” photos and 3, 2 1/2 “ x 3 1 / 2” negatives."""

ocr2 = """UNCLASSIFIEd
AF FORM 112-PART 11
(CLASSIFICATION)
APPROVED 1 JUNE 1948
AIR INTELLIGENCE INFORMATION REPORT
FROM
REPORT NO.
PAR TWO
Det 4, 10 6th AISS
AISS-UFCB-387-57
PAGE
5
OF
8
PAGES
S-T--1-0--N-T
I went outside the We ther Station about 1550 PST to
observe the thunderstorm to the northeast. This thunderstorm
was estimated to be approximately 10 miles to the northeast.
While watching for lightning and trying to determine the
direction of movement of the storm, several very I Est noving
objects we e seen at the west edge of the storm. They we e
moving very r. cidly back and forth uch like à mock-dog fight.
They changed directions Instantaneoisl and appeared mich larger
momentarily during their turns. They stayed in view over
minute and I finally lost sight of them in the storm. Visibility
was excellent during the entire period.
Lewis F. Baker AO 490014
Major, JSAF
A CERTIFIED TRUE COPY
RICHARD ade HOLM
NO, W-1, USAF
NOTE: THIS DOCUMENT CONTAINS INFORMATION AFFECTING THE NATIONAL DEFENSE OF THE UNITED STATES WITHIN THE MEANING OF THE ESPIONAGE ACT. 50 U S.
31 AND 32 AS AMENDED. ITS TRANSMISSION OR THE REVELATION OF ITS CONTENTS IN ANY MANNER TO AN UNAUTHORIZED PERSON IS PROHIBITED BY LAW.
IT. MAY NOT BE REPRODUCED IN WHOLE OR IN PART. BY OTHER THAN UNITED STATES AIR FORCE AGENCIES. EXCEPT BY PERMISSION OF THE DIRECTOR OF
INTELLIGENCE USAF.
UNCLASSIFIED
(CLASSIFICATION)
18--58570-1
*
PRINTING
OFFICE"""

human2 = """UNCLASSIFIED  
AF FORM 112-PART II  
(CLASSIFICATION)  
APPROVED 1 JUNE 1948  
AIR INTELLIGENCE INFORMATION REPORT  
FROM  
REPORT NO.  
PART TWO  
Det 4, 10 6th AISS  
AISS-UFCB-387-57  
PAGE  
5  
OF  
8  
PAGES  
S-T--1-0--N-T  

I went outside the Weather Station about 1550 PST to observe the thunderstorm to the northeast. This thunderstorm was estimated to be approximately 10 miles to the northeast. While watching for lightning and trying to determine the direction of movement of the storm, several very fast moving objects were seen at the west edge of the storm. They were moving very rapidly back and forth, much like a mock-dog fight. They changed directions instantaneously and appeared much larger momentarily during their turns. They stayed in view over a minute and I finally lost sight of them in the storm. Visibility was excellent during the entire period.  

Lewis F. Baker AO 490014  
Major, USAF 
A CERTIFIED TRUE COPY  
RICHARD A HOLM  
WO, W-1, USAF  

NOTE: THIS DOCUMENT CONTAINS INFORMATION AFFECTING THE NATIONAL DEFENSE OF THE UNITED STATES WITHIN THE MEANING OF THE ESPIONAGE ACT. 50 U.S.C-. 31 AND 32 AS AMENDED. ITS TRANSMISSION OR THE REVELATION OF ITS CONTENTS IN ANY MANNER TO AN UNAUTHORIZED PERSON IS PROHIBITED BY LAW. IT MAY NOT BE REPRODUCED IN WHOLE OR IN PART, BY OTHER THAN UNITED STATES AIR FORCE AGENCIES, EXCEPT BY PERMISSION OF THE DIRECTOR OF INTELLIGENCE USAF.  
UNCLASSIFIED  
(CLASSIFICATION)  
18--58570-1  
*  
U.S. GOVERNMENT PRINTING OFFICE"""

ocr3 = """the
5875
st
= 0658-
72721
HENKSVILLE (CAR)
4480
Hanksville
R
20
HANHSVULE RADIO
MaSai
491
.
.10
-
MOUNTRICTION
150
7151
MJ
11485
R
eian
KJ
LJ
C
38
2.
50
10
50
10
a
40
20
30
40
50
11320
=
8987
-
10650
-
Monticelio
9202
o
PK
HITE PARKER
7930
50
01445
3549 35
Dove
Creek
8150
9059
Blanding
BLANDING
5750-25
YÉLLOW
8920
-
30
-
1
20
Bluff
6443
MEXICAN HAT
4250-25
KH
c
OLJETO (Pvi) MONUMENTVALLEY
483811-36
15155
LH
MH
10388
UTAH
-
37
ARIZONA
Mexican nater
TES NOS PAS
E
a
-
7097
50
RASTORALP
66333
9420
7900
(ROCK POINT MISSION
Kayenta
5100
20
KAYENTA
5810--56
40
!
KAIBITO
is
070--26
c
ROUND ROCK
.COVE
5400 -3-33
60s0
30
9835
l
0
-10
-
8075
.7035
Tonalea
20
MANY FARMS
-
300--24
-
-
7580
TY
CHINLE
44
10
5500 50
7580
Chinie
Moenhopi
KG
to
G
-
11
Let.
36
To Valle 115. VLE 20
50
30
40
10
20
30
50
14
40
50
ALTITUDE CONVERSION SCALE
Meters
To Winslogg 266 INW #
10
15
20
25
30
J
&
20
Feet
30
40
50
60
70
80
90
100
For conversions above 100 leet. add like numrer of ciphers to the figures on bothsides of scale.
I
111°K
110 L
(Joins 405) 109 M
410
430
4:
0
2401
2501
260
270
280
290
300
310
320,
330
340)
350
360
370
380
390
400
420
130
140
150
160
170
180
190
200
210
220
230
150
160
170)
1801
1901
200
210
2201
230
240
2501
260
270
or
st and Geodetic Survey
herce
The
NOTE: It is requested that users of this chart indicate corrections and additions
which come to their attention and notily
"THE DIRECTOR, U.S. COAST AND GEODETIC SURVEY, WASHINGTON 25, D.C."
BASE NO 5R2
Obstructions
OLLED AREAS
stations. Limits of
500 feet or higher above ground
Under construction, position
UC
of the radials.
Less than 500 feet above ground
and elevation unverified"""

human3 = "ǂmapǂ"


print(f"Cleaned version of OCR1: \n{clean_string(ocr1)}")
print(f"Cleaned version of human 1: \n {clean_string(human1)}")
print()
print(f"Cleaned version of OCR2: \n{clean_string(ocr2)}")
print(f"Cleaned version of human 2: \n{clean_string(human2)}")
print()
print(f"Cleaned version of OCR3: \n{clean_string(ocr3)}")
print(f"Cleaned version of human 3: \n{clean_string(human3)}")



print(f"Distance 1: {distance(ocr1, human1)}")
print(f"Distance 2: {distance(ocr2, human2)}")
print(f"Distance 3: {distance(ocr3, human3)}")

print(f"CER 1: {character_error_rate(ocr1, human1)}")
print(f"CER 2: {character_error_rate(ocr2, human2)}")
print(f"CER 3: {character_error_rate(ocr3, human3)}")

print(f"Length of OCR 1 {len(clean_string(ocr1))}")
print(f"Length of Human 1 {len(clean_string(human1))}")
print(f"Length of OCR 2 {len(clean_string(ocr2))}")
print(f"Length of Human 2 {len(clean_string(human2))}")
print(f"Length of OCR 3 {len(clean_string(ocr3))}")
print(f"Length of Human 3 {len(clean_string(human3))}")





# ref = "Hello ǂthis should be ignoredǂ world ʘkeep thisʘ!"
# hyp = "Helo ʘkeep thisʘ wurld ǂremoveǂ"

# print(clean_string(ref))
# print(clean_string(hyp))

# cer = character_error_rate(ref, hyp)
# print(f"CER: {cer:.3f}")

# human = """This case contains 2, 5" x 7" photos and 3, 2 1/2 " x 3 1 / 2" negatives."""
# gpt4osimple = "This case contains 2.5% of photos and 3 negatives."

# print(f"CER: {character_error_rate(human,gpt4osimple):.3f}")





