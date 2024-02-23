import React, { useState } from 'react';
import './App.css';

function AppOld() {
  const [file, setFile] = useState(null);
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleQueryChange = (e) => {
    setQuery(e.target.value);
  };

  const uploadFile = async () => {
    const formData = new FormData();
    formData.append('file', file);
    console.info("formData",formData);
     await fetch('http://localhost:5000/upload', { mode:'no-cors',
      method: 'POST',
      body: formData,
    })
    .then(response => {
      console.log("RESPONSE ", response);
      console.log("RESPONSE.OK ", response.ok);
      console.log("RESPONSE.STATUS ", response.status);
      console.log("RESPONSE.STATUS TEXT ", response.statusText);
      console.log("RESPONSE.HEADERS ", response.headers);
      console.log("RESPONSE.TYPE ", response.type);
      console.log("RESPONSE.URL ", response.url);
      console.log("RESPONSE.REDIRECTED ", response.redirected);
      console.log("RESPONSE.SIZE ", response.size);
      console.log("RESPONSE.BODY ", response.body);
      console.log("RESPONSE.BODY USED ", response.bodyUsed);
      console.log("RESPONSE.FORM DATA ", response.formData);
      console.log("RESPONSE.ARRAY BUFFER ", response.arrayBuffer);
      console.log("RESPONSE.BLOB ", response.blob);
      console.log("RESPONSE.TEXT ", response.text);
      console.log("RESPONSE.JSON ", response.json);
      console.log("RESPONSE.DATA ", response.data);
      console.log("RESPONSE.ERROR ", response);

      if (!response.ok) {
        throw new Error(`API call failed with status ${response.status}`);
      }
      return response.json();
    })
    .then(responseData => {
      console.log("RESPONSE DATA ", responseData);
      setFile(null);
    })
  };

  const searchDocuments = async () => {
    console.info("QUERY",query);
    console.info("JSON", JSON.stringify({ query }));
      await fetch("http://localhost:5000/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(query)
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`API call failed with status ${response.status}`);
        }
        return response.json();
      })
      .then(responseData => {
        console.log("Request successful!");
        // Handle response data
        console.log("RESPONSE DATA ", responseData);
        setResponse(responseData.response);
        setSearchResults(responseData.search_results);
      })
      .catch(error => {
        console.error("Error:", error);
      });
  };

  return (
    <div className="App">
      <h1>Document Search Bot</h1>

      <div>
        <input type="file" onChange={handleFileChange} />
        <button onClick={uploadFile}>Upload</button>
      </div>

      <div>
        <input type="text" placeholder="Enter your query" value={query} onChange={handleQueryChange} />
        <button onClick={searchDocuments}>Search</button>
      </div>
      <div>
        <h3>Response: {response}</h3>
        <h3>Search Results:</h3>
        <ul>
          {searchResults.map((result, index) => (
            <li key={index}>{result.file_path}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default AppOld;
