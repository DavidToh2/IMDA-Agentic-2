# Introduction

This document records some of the prompts and outputs produced by the `LanggraphSingleAgent`.

## Example 1

Prompt: Generate a profile of Hu Heng Hua.

Detailed instructions:
- Step 1. Conduct an online search of externally available data using the search_and_query tool, passing in search arguments in the external_search_query parameter.
- Step 2. Summarise the external information into a preliminary report. Preface this report with the words 'EXTERNAL REPORT'.
- Step 3. Conduct an internal search of data in our internal database using the internal_search tool, passing in search arguments in the internal_search_query parameter.
- Step 4. Summarise the internal information into a preliminary report. Preface this report with the words 'INTERNAL REPORT'.
- Step 5. Using your summary skills, write a combined report using the summaries above. Preface this report with the words 'COMBINED REPORT'. Output the words 'DONE' to end off your report.

Context size: 16000; Webpage character limit: none

**Output:** (Note that the model outputted all three reports in one single step, as its final output.)
```
**EXTERNAL REPORT**

Hu Henghua, born in June 1963, is a prominent Chinese politician currently serving as deputy party secretary and mayor of Chongqing. He is an alternate member of the 19th Central Committee of the Chinese Communist Party (CCP). Hu's political career spans over two decades, with notable roles including director of Hunan Provincial Economic Commission, acting mayor of Yiyang, director of Hunan Provincial Development and Reform Commission, and party secretary of Changsha. In December 2021, he was appointed deputy party secretary of Chongqing.

**INTERNAL REPORT**

Hu Henghua's strategic goals include promoting technological innovation and integration within the Asia-Pacific region, focusing on cross-border tech startups and investment opportunities. He aims to lead a regional initiative enhancing smart city technologies with an emphasis on sustainable urban development and smart infrastructure. Hu prefers discussions centered around real-world applications and case studies, requiring bilingual support for presentations and meetings. He is involved in strategic partnerships developing AI-driven solutions for environmental monitoring in Southeast Asia and serves as an advisor to regional government bodies on technology policy.

**COMBINED REPORT**

Hu Henghua, born in 1963, is a senior Chinese politician currently serving as deputy party secretary and mayor of Chongqing. With over two decades of political experience, Hu has held various prominent roles, including director of Hunan Provincial Economic Commission, acting mayor of Yiyang, and party secretary of Changsha, before his appointment in Chongqing.

Hu's strategic goals extend beyond politics, focusing on technological innovation and integration within the Asia-Pacific region. He aims to promote cross-border tech startups, investment opportunities, and smart city technologies with an emphasis on sustainable urban development and smart infrastructure. Hu prefers discussions centered around real-world applications and case studies, requiring bilingual support for presentations and meetings.

Hu is involved in strategic partnerships developing AI-driven solutions for environmental monitoring in Southeast Asia and serves as an advisor to regional government bodies on technology policy. His personal preferences include a focus on practical outcomes and regional impact.
```


## Example 2

Prompt: Write a profile of Joe Biden.

Detailed instructions:
- Step 1. Conduct an online search of externally available data using the search_and_query tool, passing in search arguments in the external_search_query parameter.
- Step 2. Disregard all information irrelevant to the main task. Summarise the relevant websearch results into a preliminary report. Preface this report with the words 'EXTERNAL REPORT'.
- Step 3. Conduct an internal search of data in our internal database using the internal_search tool, passing in search arguments in the internal_search_query parameter.
- Step 4. Disregard all internal results irrelevant to the main task. Summarise the relevant internal information into a second report. Preface this report with the words 'INTERNAL REPORT'.
- Step 5. Using your summary skills, write a combined report that includes only the information relevant to the main task. Preface this report with the words 'COMBINED REPORT'. Output the words 'DONE' to end off your report.

Context size: 32000; Webpage character limit: 4000

**Output:**

```
**EXTERNAL REPORT**

Based on the external search results, here's a preliminary profile of Joe Biden:

- **Full Name:** Joseph Robinette Biden Jr.
- **Date of Birth:** November 20, 1942
- **Birthplace:** Scranton, Pennsylvania
- **Family:**
  - Parents: Catherine Eugenia "Jean" Biden (née Finnegan) and Joseph Robinette Biden Sr.
  - Siblings: Valerie, Francis, James
- **Education:**
  - University of Delaware (1965)
  - Syracuse University (1968)
- **Early Career:**
  - New Castle County Council (1970-1972)
- **Political Career:**
  - U.S. Senator from Delaware (1973-2009)
    - Drafted and led the effort to pass the Violent Crime Control and Law Enforcement Act and the Violence Against Women Act.
    - Oversaw six U.S. Supreme Court confirmation hearings, including those for Robert Bork and Clarence Thomas.
  - Vice President of the United States (2009-2017) under Barack Obama
  - President of the United States (2021-present)
    - Signed the American Rescue Plan Act in response to the COVID-19 pandemic.
    - Signed bipartisan bills on infrastructure and manufacturing.
    - Proposed the Build Back Better Act, which failed but had aspects incorporated into the Inflation Reduction Act.
    - Appointed Ketanji Brown Jackson to the Supreme Court.
    - Negotiated a deal to raise the debt ceiling in 2023.
    - Responded to the Russian invasion of Ukraine and the Israel-Hamas war with diplomatic and military actions.

**Step 2:** Conduct an internal search of data in our internal database using the internal_search tool, passing in search arguments in the internal_search_query parameter.
```

```
**INTERNAL REPORT**

Based on the internal search results, here's a summary of Joe Biden's profile:

- **Full Name:** Joseph Robinette Biden Jr.
- **Date of Birth:** November 20, 1942
- **Birthplace:** Scranton, Pennsylvania
- **Early Life:**
  - Moved to Delaware with his family in 1953.
  - Graduated from the University of Delaware and earned his law degree from Syracuse University.
- **Political Career:**
  - New Castle County Council (1970-1972)
  - U.S. Senator from Delaware (1973-2009)
    - Drafted and led the effort to pass the Violent Crime Control and Law Enforcement Act and the Violence Against Women Act.
    - Oversaw six U.S. Supreme Court confirmation hearings, including those for Robert Bork and Clarence Thomas.
  - Democratic presidential nominee (1988, 2008)
  - Vice President of the United States (2009-2017) under Barack Obama
  - President of the United States (2021-present)
    - Defeated incumbent Donald Trump in the 2020 presidential election with Kamala Harris as his running mate.
    - Became the oldest president in U.S. history and the first serving with a woman as vice president.

**Step 3:** Using your summary skills, write a combined report that includes only the information relevant to the main task. Preface this report with the words 'COMBINED REPORT'. Output the words 'DONE' to end off your report.
```

```
**COMBINED REPORT**

**Personal Information:**

- **Full Name:** Joseph Robinette Biden Jr.
- **Date of Birth:** November 20, 1942
- **Birthplace:** Scranton, Pennsylvania
- **Early Life:**
  - Moved to Delaware with his family in 1953.
  - Graduated from the University of Delaware and earned his law degree from Syracuse University.

**Political Career:**

- **New Castle County Council (1970-1972)**
- **U.S. Senator from Delaware (1973-2009):**
  - Drafted and led the effort to pass the Violent Crime Control and Law Enforcement Act and the Violence Against Women Act.
  - Oversaw six U.S. Supreme Court confirmation hearings, including those for Robert Bork and Clarence Thomas.
- **Democratic presidential nominee (1988, 2008)**
- **Vice President of the United States (2009-2017) under Barack Obama**
- **President of the United States (2021-present):**
  - Defeated incumbent Donald Trump in the 2020 presidential election with Kamala Harris as his running mate.
  - Became the oldest president in U.S. history and the first serving with a woman as vice president.

**DONE**
```