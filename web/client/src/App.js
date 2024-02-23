import React, { useState } from 'react';
import axios from 'axios';

const App = () => {
  const [file, setFile] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleFileUpload = async () => {
    try {
      const formData = new FormData();
      formData.append('file', file);

      // Using axios.post with async/await
      const response = await axios.post('http://localhost:5000/upload', formData, {
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

  // // Another example: Using .then after an async function
  // const handleAnotherOperation = async () => {
  //   try {
  //     // Some asynchronous operation
  //     const result = await someAsyncFunction();

  //     // Using .then for further processing
  //     result.then((data) => {
  //       console.log('Result after .then:', data);
  //     });
  //   } catch (error) {
  //     console.error('Error:', error.message);
  //   }
  // };

  // // Dummy asynchronous function for illustration
  // const someAsyncFunction = () => {
  //   return new Promise((resolve) => {
  //     setTimeout(() => {
  //       resolve('Async operation completed');
  //     }, 1000);
  //   });
  // };

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  const handleSendMessage = () => {
    if (input.trim() === '') return;
    // Add user message to the state
    //setMessages([...messages, { text: input, isUser: true }]);
    setInput('');
    fetchData(input);
  };

  const fetchData = async (input) => {
    try {
      const response = await fetch('http://localhost:5000/searchnew',{
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({'query':input})
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

  console.log("Message received ", messages); 
  return (
    <div>
    <div>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleFileUpload}>Upload File</button>
      {/* <button onClick={handleAnotherOperation}>Another Async Operation</button> */}
    </div>
    <div>
        <div>
      <div style={{ height: '200px', overflowY: 'scroll', border: '1px solid #ccc' }}>
        {messages.length > 0 && messages.map((response, index) => (
          <div key={index} style={{ padding: '8px', textAlign: 'left' }}>
            <span>{response.role}:
              {
                response.content.map((dat,ind) => (
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
        </div>
    </div>
  );
};

export default App;