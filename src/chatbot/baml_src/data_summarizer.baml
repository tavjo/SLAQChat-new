
function SummarizeData(inputMessage: Payload) -> DataSummarizer {
    client Reasoner
    prompt #"
      {{ GetSystemPrompt() }}
      {{ GetNExtSEEKIntro() }}

    Analyze the conversation and create a concise but informative summary to answer the user's query. 

    You must also use the resources provided as additional context to you to answer the user's query.
    
    Focus on:
    1. Key points relevant to the user's query
    2. Important details from available resources
    3. Your summary should attempt to answer the user's query based on the information available
    4. Never make up information, only use the information provided
    5. Format your response as if addressing the user directly

    User Query:
    {{ inputMessage.user_query }}


    Resources:
    {{ inputMessage.resource }}

    Messages:
    {{ PrintMessages(inputMessage.aggregatedMessages) }}

    {{ ctx.output_format }}
    "#
}

test BasicSummary {
  functions [SummarizeData]
  args {
    inputMessage {
      user_query "Can you help me find protocols related to RNA extraction from blood samples?"
      aggregatedMessages [
        {
          name "user"
          message "Can you help me find protocols related to RNA extraction from blood samples?"
          role "user"
        }
      ]
      last_worker "user"
    }
  }
}

test ComplexSummary {
  functions [SummarizeData]
  args {
    inputMessage {
      user_query "I need the protocol from sample MIT-123 and its metadata"
      aggregatedMessages [
        {
          name "protocol_retriever"
          message "I retrieved the protocol for sample MIT-123 and its metadata"
          role "assistant"
        }
      ]
      last_worker "protocol_retriever"
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