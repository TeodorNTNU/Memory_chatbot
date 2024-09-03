//  // ChatWindow.jsx
//  import React from 'react';
//  import '../styles/ChatWindow.css';
//  
//  const ChatWindow = ({ messages, loading, error }) => {
//    console.log("Rendering ChatWindow with messages:", messages);
//  
//    // Ensure messages is an array and not null or undefined
//    const validMessages = Array.isArray(messages) ? messages : [];
//  
//    return (
//      <div className="chat-container">
//        {/* Chat Window */}
//        <div className="chat-window">
//          <h2>Chat</h2>
//  
//          {/* Show error message if there's an error */}
//          {error && <p className="error">{error.message || 'An error occurred.'}</p>}
//  
//          {/* Render messages if loaded and no error */}
//          {!loading && !error && (
//            <div className="messages-container">
//              {/* Scrollable message area */}
//              <div className="messages-scrollable">
//                {validMessages.length === 0 ? (
//                  <p>No messages available.</p>
//                ) : (
//                  validMessages.map((msg, index) => {
//                    // Check if msg is an object and has correct keys
//                    if (typeof msg !== 'object' || msg === null) {
//                      console.warn('Invalid message format at index', index, ':', msg);
//                      return null; // Skip rendering this message
//                    }
//  
//                    // Helper function to safely get the string value
//                    const safeRenderText = (value) => {
//                      if (Array.isArray(value) && value.length > 0) {
//                        return value[0] !== null && value[0] !== undefined ? String(value[0]) : null;
//                      }
//                      return typeof value === 'string' ? value : null;
//                    };
//  
//                    const userResponse = safeRenderText(msg.user_response);
//                    const aiResponse = safeRenderText(msg.ai_response);
//  
//                    return (
//                      <div key={index} className="message">
//                        {/* Render user message if it exists */}
//                        {userResponse && (
//                          <div className="message user">
//                            <span><strong>User:</strong> {userResponse}</span>
//                          </div>
//                        )}
//  
//                        {/* Render AI message if it exists */}
//                        {aiResponse && (
//                          <div className="message ai">
//                            <span><strong>AI:</strong> {aiResponse}</span>
//                          </div>
//                        )}
//                      </div>
//                    );
//                  })
//                )}
//              </div>
//            </div>
//          )}
//  
//          {/* Loading indicator positioned at the bottom-left corner */}
//          {loading && (
//            <div className="typing-indicator">
//              <p>TeoBot is typing...</p>
//              <div className="loading-buttons">
//                <div className="loading-button" />
//                <div className="loading-button" />
//                <div className="loading-button" />
//              </div>
//            </div>
//          )}
//        </div>
//      </div>
//    );
//  };
//  
//  export default ChatWindow;

// import React from 'react';
// import '../styles/ChatWindow.css';
// 
// const ChatWindow = ({ messages, loading, error }) => {
//   console.log("Rendering ChatWindow with messages:", messages);
// 
//   // Ensure messages is an array and not null or undefined
//   const validMessages = Array.isArray(messages) ? messages : [];
// 
//   return (
//     <div className="chat-container">
//       {/* Chat Window */}
//       <div className="chat-window">
//         <h2>Chat</h2>
// 
//         {/* Show error message if there's an error */}
//         {error && <p className="error">{error.message || 'An error occurred.'}</p>}
// 
//         {/* Render messages if loaded and no error */}
//         {!loading && !error && (
//           <div className="messages-container">
//             {/* Scrollable message area */}
//             <div className="messages-scrollable">
//               {validMessages.length === 0 ? (
//                 <p>No messages available.</p>
//               ) : (
//                 validMessages.map((msg, index) => {
//                   const userResponse = msg.user_response;
//                   const aiResponse = msg.ai_response;
// 
//                   return (
//                     <div key={index} className="message">
//                       {/* Render user message if it exists */}
//                       {userResponse && (
//                         <div className="message user">
//                           <span><strong>User:</strong> {userResponse}</span>
//                         </div>
//                       )}
// 
//                       {/* Render AI message if it exists */}
//                       {aiResponse && (
//                         <div className="message ai">
//                           <span><strong>AI:</strong> {aiResponse}</span>
//                         </div>
//                       )}
//                     </div>
//                   );
//                 })
//               )}
//             </div>
//           </div>
//         )}
// 
//         {/* Loading indicator positioned at the bottom-left corner */}
//         {loading && (
//           <div className="typing-indicator">
//             <p>TeoBot is typing...</p>
//             <div className="loading-buttons">
//               <div className="loading-button" />
//               <div className="loading-button" />
//               <div className="loading-button" />
//             </div>
//           </div>
//         )}
//       </div>
//     </div>
//   );
// };
// 
// export default ChatWindow;
// 


// ChatWindow.jsx
import React from 'react';
import '../styles/ChatWindow.css';

const ChatWindow = ({ messages, loading, error }) => {
  console.log("Rendering ChatWindow with messages:", messages);

  // Ensure messages is an array and not null or undefined
  const validMessages = Array.isArray(messages) ? messages : [];

  return (
    <div className="chat-container">
      {/* Chat Window */}
      <div className="chat-window">
        <h2>Chat</h2>

        {/* Show error message if there's an error */}
        {error && <p className="error">{error.message || 'An error occurred.'}</p>}

        {/* Show loading state */}
        {loading && (
          <div className="typing-indicator">
            <p>TeoBot is typing...</p>
            <div className="loading-buttons">
              <div className="loading-button" />
              <div className="loading-button" />
              <div className="loading-button" />
            </div>
          </div>
        )}

        {/* Render messages if loaded and no error */}
        {!loading && !error && (
          <div className="messages-container">
            {/* Scrollable message area */}
            <div className="messages-scrollable">
              {validMessages.length === 0 ? (
                <p>No messages available.</p>
              ) : (
                validMessages.map((msg, index) => {
                  return (
                    <div key={index} className="message">
                      {/* Render user message if it exists */}
                      {msg.user_response && (
                        <div className="message user">
                          <span><strong>User:</strong> {msg.user_response}</span>
                        </div>
                      )}

                      {/* Render AI message if it exists */}
                      {msg.ai_response && (
                        <div className="message ai">
                          <span><strong>AI:</strong> {msg.ai_response}</span>
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatWindow;
