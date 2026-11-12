"""Benchmark test dataset for entity recognition evaluation.

Contains bilingual test cases (English and Danish) designed to evaluate
accuracy on full names, honorifics (Ms, Dr, Prof, Hr, Fru), false positives
(scientific terms, street names, corporate labels), and edge cases.
"""

from __future__ import annotations

from typing import Any, Dict, List

TEST_DATASET: List[Dict[str, Any]] = [
    {
        "text": "Ms Mette Frederiksen is in New York today.",
        "persons": ["Mette Frederiksen"],
    },
    {
        "text": "Einstein and von Neumann meet each other.",
        "persons": ["Einstein", "von Neumann"],
    },
    {
        "text": "Dr. Jane Goodall spoke with Prof. Brian Cox after the event.",
        "persons": ["Jane Goodall", "Brian Cox"],
    },
    {
        "text": "I ran the Einstein sum on the dataset, then exported the report.",
        "persons": [],
    },
    {
        "text": "Mrs. Oprah Winfrey thanked Mr. John Legend for the introduction.",
        "persons": ["Oprah Winfrey", "John Legend"],
    },
    {
        "text": "The package was signed by A. Smith, but the label says 'Smithson Tools'.",
        "persons": ["A. Smith"],
    },
    {
        "text": "We discussed Ada Lovelace Jr. in class, but the slides were titled 'Lovelace Framework'.",
        "persons": ["Ada Lovelace Jr."],
    },
    {
        "text": "Captain Jean-Luc Picard reviewed the Picard protocol.",
        "persons": ["Jean-Luc Picard"],
    },
    {
        "text": "I emailed Mr. Tim Cook and Sundar Pichai about the schedule.",
        "persons": ["Tim Cook", "Sundar Pichai"],
    },
    {
        "text": "The mural by Banksy was mentioned, but no one knows the real name.",
        "persons": ["Banksy"],
    },
    {
        "text": "Yesterday, Serena Williams joined Rafael Nadal on stage.",
        "persons": ["Serena Williams", "Rafael Nadal"],
    },
    {
        "text": "We met with Ms. Mary-Jane Watson; later we saw the Watson & Co. sign.",
        "persons": ["Mary-Jane Watson"],
    },
    {
        "text": "The station is called Newton Road, not 'Isaac Newton'.",
        "persons": [],
    },
    {
        "text": "Mr. Keanu Reeves was mistaken for 'Reeves Boulevard' on the map.",
        "persons": ["Keanu Reeves"],
    },
    {
        "text": "I read a quote by Søren Kierkegaard and one by Hannah Arendt.",
        "persons": ["Søren Kierkegaard", "Hannah Arendt"],
    },
    {
        "text": "Please forward this to Dr. Martin Luther King Jr., if you have his contact.",
        "persons": ["Martin Luther King Jr."],
    },
    {
        "text": "The seminar featured von der Leyen and Emmanuel Macron.",
        "persons": ["von der Leyen", "Emmanuel Macron"],
    },
    {
        "text": "We used the Turing test example, but Alan Turing was not the topic today.",
        "persons": ["Alan Turing"],
    },
    {
        "text": "I bought a 'Tesla' mug; Nikola Tesla wasn't mentioned anywhere on it.",
        "persons": ["Nikola Tesla"],
    },
    {
        "text": "Ms. Angelina Jolie visited the clinic; the sign outside reads 'Jolie Care'.",
        "persons": ["Angelina Jolie"],
    },
    {
        "text": "I saw 'Einstein Café' and thought of Albert Einstein.",
        "persons": ["Albert Einstein"],
    },
    {
        "text": "Barack Obama and Michelle Obama recorded a joint message.",
        "persons": ["Barack Obama", "Michelle Obama"],
    },
    {
        "text": "Mr. José Mourinho Jr. arrived late, but Mourinho Street was closed anyway.",
        "persons": ["José Mourinho Jr."],
    },
    {
        "text": "The library named after Virginia Woolf hosted a talk by Neil Gaiman.",
        "persons": ["Virginia Woolf", "Neil Gaiman"],
    },
    {
        "text": "We compared 'Darwin OS' with Linux; Charles Darwin was only a footnote.",
        "persons": ["Charles Darwin"],
    },
    {
        "text": "The letter was addressed to Prof. Noam Chomsky, care of Chomsky Hall.",
        "persons": ["Noam Chomsky"],
    },
    {
        "text": "I messaged Mr. Elon Musk, but the reply came from 'Musk Logistics'.",
        "persons": ["Elon Musk"],
    },
    {
        "text": "Mrs. Malala Yousafzai met with Greta Thunberg in Oslo.",
        "persons": ["Malala Yousafzai", "Greta Thunberg"],
    },
    {
        "text": "Hr. Lars Løkke Rasmussen deltog i mødet i dag.",
        "persons": ["Lars Løkke Rasmussen"],
    },
    {
        "text": "Fru Helle Thorning-Schmidt besøgte campus, men skiltet sagde 'Thorning Plads'.",
        "persons": ["Helle Thorning-Schmidt"],
    },
    {
        "text": "Betzy Meyers Høj i Ballerup er spærret på grund af vejarbejde.",
        "persons": [],
    },
    {
        "text": "Jeg så Mads Mikkelsen på plakaten, men det var bare 'Mikkelsen & Søn'.",
        "persons": ["Mads Mikkelsen"],
    },
    {
        "text": "Ms. Pia Kjærsgaard holdt tale, og bagefter gik vi forbi Kjærsgaard Allé.",
        "persons": ["Pia Kjærsgaard"],
    },
    {
        "text": "Professor Niels Bohr nævnes ofte, men her handler det om Bohr-variablen i koden.",
        "persons": ["Niels Bohr"],
    },
    {
        "text": "Vi drak kaffe på 'Andersen Café'—ikke noget med H.C. Andersen i teksten.",
        "persons": ["H.C. Andersen"],
    },
    {
        "text": "Jeg mødte Sofie Linde og Jakob Ellemann-Jensen ved indgangen.",
        "persons": ["Sofie Linde", "Jakob Ellemann-Jensen"],
    },
    {
        "text": "Dr. Anders Fogh Rasmussen kom for sent, fordi Foghvej var lukket.",
        "persons": ["Anders Fogh Rasmussen"],
    },
    {
        "text": "Kald lige på frk. Karen Blixen, hvis hun er i bygningen.",
        "persons": ["Karen Blixen"],
    },
    {
        "text": "Vi snakkede om 'einstein sum' i regnearket, ikke om Albert Einstein.",
        "persons": [],
    },
    {
        "text": "Statsminister Mette Frederiksen og Kong Frederik mødtes til receptionen.",
        "persons": ["Mette Frederiksen", "Kong Frederik"],
    },
]

