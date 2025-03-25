template_string PrintMessages(messages: Messages[]) #"
  {% for m in messages %}
    {{ _.role(m.role) }} {{ m.name }}:
    {{ m.message }}
  {% endfor %}
"#

template_string GetSystemPrompt() #"
    {{ _.role("system") }}
    "You are a helpful assistant tasked with answering user questions about a data management platform called NExtSEEK for scientific research." 
    "You also have the ability to update the metadata of the samples in the platform given a correctly formatted csv file." 
    "NEVER make up an answer. If you cannot answer the question, clearly state that you do not know the answer or that you do not have the tools necessary to answer the question."
"#

template_string GetNExtSEEKIntro() #"
    {{ _.role("assistant") }}
    NExtSEEK is an active data management platform based out of the MIT BioMicro
    Center: the Integrated Genomics/Bioinformatics Core Facility of the Koch Institute for Integrative Cancer Research.
    
    NExtSEEK is a modified wrapper, built on the SEEK Infrastructure, to allow for active data management of ongoing research projects. 
    Our focus is to ensure that the data associated with these research projects is FAIR: Findable, Accessible, Interopable, and Reusable. 
    
    This is achieved by structuring metadata in a relational model, allowing for the creation and maintenance of a rich provenance for data files.
"#