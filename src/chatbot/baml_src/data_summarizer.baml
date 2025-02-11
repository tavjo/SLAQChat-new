
function SummarizeData(inputMessage: Messages) -> DataSummarizer {
    client MyClient
    prompt #"
    Analyze the conversation and create a concise summary. Focus on:
    1. Key points relevant to the user's query
    2. Important details from available resources
    {{ ctx.output_format }}
    {{ _.role("system") }}
    Messages:
    {% for msg in inputMessage.aggregatedMessages %}
    {{ _.role(inputMessage.system_message) }} {{ msg }} 
    {% endfor %}
    {{ _.role("user") }} {{ inputMessage.user_query }}
    {% if inputMessage.resource %}
    Available Resources:
    {{ inputMessage.resource }}
    {% endif %}
    "#
}

test BasicSummary {
  functions [SummarizeData]
  args {
    inputMessage {
      user_query "Can you help me find protocols related to RNA extraction from blood samples?"
      system_message "Lab assistant helping with protocol searches"
      aggregatedMessages ["Can you help me find protocols related to RNA extraction from blood samples?"]
    }
  }
}

test ComplexSummary {
  functions [SummarizeData]
  args {
    inputMessage {
      user_query "I need the protocol from sample MIT-123 and its metadata"
      system_message "Lab protocol assistant"
      aggregatedMessages ["I need the protocol from sample MIT-123 and its metadata"]
      resource {
        sampleMetadata [
          {
            id "MIT-123"
            type "blood_sample"
          }
        ]
        protocolUrl "https://protocols.mit.edu/123"
        sampleUrl "https://nextseek.mit.edu/seek/sampletree/uid=MIT-123"
      }
    }
  }
}