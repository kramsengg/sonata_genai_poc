// import logo from './logo.svg';
// import './App.css';

// function App() {
//   return (
//     <div className="App">
//       <header className="App-header">
//         <img src={logo} className="App-logo" alt="logo" />
//         <p>
//           Edit <code>src/App.js</code> and save to reload.
//         </p>
//         <a
//           className="App-link"
//           href="https://reactjs.org"
//           target="_blank"
//           rel="noopener noreferrer"
//         >
//           Learn React
//         </a>
//       </header>
//     </div>
//   );
// }

// export default App;


import React, { useState } from 'react';
import './App.css';

function App() {
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
    });

    setFile(null);
  };

  const searchDocuments = async () => {
    console.info("QUERY",query);
    console.info("JSON", JSON.stringify({ query }));
    const response = await fetch('http://localhost:5000/search', {
    mode:'no-cors',  
    method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query}),
    });
    
    // if (!response.ok) {
    //   throw new Error(`Error: ${response.statusText}`);
    // }
    console.info("RESPONSE", response);
    console.info("RESPONSE JSON", response.ok);
    const data = await response.json();
    console.info("RESPONSE JSON data", data);
    
    setResponse(data.response);
    setSearchResults(data.search_results);
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

export default App;
