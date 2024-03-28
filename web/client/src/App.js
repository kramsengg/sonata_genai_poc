import React, { useState } from 'react';
import axios from 'axios';

const App = () => {
  const [file, setFile] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [activeTab, setActiveTab] = useState('documentUpload');

  const handleFileChange = (event) => {
    console.log(event.target.files[0]);
    setFile(event.target.files[0]);
  };

  const handleFileUpload = async () => {
    try {
      const formData = new FormData();
      formData.append('file', file);

      // Using axios.post with async/await
      const response = await axios.post('http://localhost:5000/uploadfile', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Handling the response
      console.log('File uploaded successfully:', response.data);
      setFile(null); // Reset the file state after successful upload
    } catch (error) {
      console.error('Error uploading file:', error.message);
    }
  };


  const setFocus = (inputId) => {
    const inputElement = document.getElementById(inputId);
    if (inputElement) {
      inputElement.focus();
      setInput(inputElement.text)
    }
  };

  const handleInputChange = (e) => {
    setInput(e.target.value);
    
  };

  const handleSendMessage = () => {
    //const inputElement = document.getElementById('searchText');
    if ( input.trim() === '') return;
    // Add user message to the state
    //setMessages([...messages, { text: input, isUser: true }]);
    setInput('');
    //fetchData(input);
    fetchDataText(input);
  };

  const fetchData = async (input) => {
    try {
      const response = await fetch('http://localhost:5000/searchnew', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 'query': input })
      });
      const result = await response.json();
      console.log(result);

      let all_mes = [];
      all_mes = JSON.parse(result);

      setMessages(all_mes.data);
      setInput('');
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const fetchDataText = async (input) => {
    try {
      const response = await fetch('http://localhost:5000/searchtext', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 'query': input })
      });
      const result = await response.json();
      console.log(result);

      //let all_mes = [];
      //all_mes = JSON.parse(result);

      //result.response.data[0].content
      setMessages(result.response.data)
      //setMessages(all_mes.data);
      setInput('');
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const DocumentUpload = () => (
    <div>
      <h2>Document Upload</h2>
      {
        /* Add your document upload logic here */
        <div>
          <input type="file" onChange={handleFileChange} />
          <button onClick={handleFileUpload}>Upload File</button>
        </div>
      }
    </div>
  );

  const ChatWindow = () => (

    <div>
      <h2>Chat Window</h2>
      {
        /* Add your chat window logic here */
        <div>
          <div style={{ height: '200px', overflowY: 'scroll', border: '1px solid #ccc' }}>
            {messages.length > 0 && messages.map((response, index) => (
              <div key={index} style={{ padding: '8px', textAlign: 'left' }}>
                <span>{response.role}:</span>
                <span>{response.content}</span>
                  {/* {
                    response.content.map((dat, ind) => (
                      <p key={ind}>{dat.text}</p>
                    ))
                  } */}
                
              </div>
            ))}
            <div>
            </div>
          </div>
          <div style={{ marginTop: '8px' }}>
            <input type="text" value={input} onChange={handleInputChange} />
            <button onClick={handleSendMessage}>Send</button>
          </div>
        </div>
      }
    </div>
  );

  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };


  console.log("Message received ", messages);

  return (
    <div>

      <div>
        <button onClick={() => handleTabChange('documentUpload')}>Document Upload</button>
        <button onClick={() => handleTabChange('chatWindow')}>Chat Window</button>
      </div>

      <div>
        {activeTab === 'documentUpload' && <DocumentUpload />}
        {activeTab === 'chatWindow' && <ChatWindow />}
      </div>


      <div>
        {/* <div>
          <input type="file" onChange={handleFileChange} />
          <button onClick={handleFileUpload}>Upload File</button>
        </div>
        <div>
          <div>
            <div style={{ height: '200px', overflowY: 'scroll', border: '1px solid #ccc' }}>
              {messages.length > 0 && messages.map((response, index) => (
                <div key={index} style={{ padding: '8px', textAlign: 'left' }}>
                  <span>{response.role}:
                    {
                      response.content.map((dat, ind) => (
                        <p key={ind}>{dat.text}</p>
                      ))
                    }
                  </span>
                </div>
              ))}
              <div>
              </div>
            </div>
            <div style={{ marginTop: '8px' }}>
              <input type="text" value={input} onChange={handleInputChange} />
              <button onClick={handleSendMessage}>Send</button>
            </div>
          </div>
        </div> */}
      </div>

    </div>
  );
};

export default App;