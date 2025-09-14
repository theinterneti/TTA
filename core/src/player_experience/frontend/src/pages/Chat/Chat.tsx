import React, { useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useSelector } from "react-redux";
// useDispatch removed - not used in this component
import { RootState } from "../../store/store";
import websocketService from "../../services/websocket";
import ChatMessage from "../../components/Chat/ChatMessage";
import TypingIndicator from "../../components/Chat/TypingIndicator";
import SkipLink from "../../components/Accessibility/SkipLink";
import ScreenReaderAnnouncement from "../../components/Accessibility/ScreenReaderAnnouncement";
import useAccessibility from "../../hooks/useAccessibility";
import useMobile from "../../hooks/useMobile";

const Chat: React.FC = () => {
  const { sessionId } = useParams<{ sessionId?: string }>();
  const navigate = useNavigate();
  // Dispatch removed - not used in this component
  const {
    // currentSession, // Not used in this component
    messageHistory,
    isConnected,
    isTyping,
    connectionError,
  } = useSelector((state: RootState) => state.chat);
  const { selectedCharacter } = useSelector(
    (state: RootState) => state.character
  );
  const { profile } = useSelector((state: RootState) => state.player);

  const [inputValue, setInputValue] = useState("");
  const [isInputFocused, setIsInputFocused] = useState(false);
  const [announcement, setAnnouncement] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  const { preferences, announce } = useAccessibility();
  const { isMobile, touchSupported } = useMobile();
  // isTablet and orientation removed - not used in this component

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    const scrollBehavior = preferences.reduceMotion ? "auto" : "smooth";
    messagesEndRef.current?.scrollIntoView({ behavior: scrollBehavior });
  }, [messageHistory, isTyping, preferences.reduceMotion]);

  // Announce new messages to screen readers
  useEffect(() => {
    if (messageHistory.length > 0) {
      const lastMessage = messageHistory[messageHistory.length - 1];
      if (lastMessage.type === "assistant" || lastMessage.type === "system") {
        setAnnouncement(`New message: ${lastMessage.content}`);
        announce(`New message from assistant: ${lastMessage.content}`);
      }
    }
  }, [messageHistory, announce]);

  useEffect(() => {
    // Connect to WebSocket with player ID and session ID
    const playerId = profile?.player_id;
    if (sessionId && playerId) {
      websocketService.connect(sessionId, playerId);
    } else {
      console.error("Missing required parameters for WebSocket connection:", {
        sessionId,
        playerId,
      });
    }

    return () => {
      websocketService.disconnect();
    };
  }, [sessionId, profile?.player_id]);

  const handleSendMessage = (content: string) => {
    if (!content.trim() || !isConnected) return;

    websocketService.sendMessage(content.trim(), {
      character_id: selectedCharacter?.character_id,
      player_id: profile?.player_id,
    });
    setInputValue("");
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(inputValue);
    } else if (e.key === "Escape") {
      // Clear input on escape
      setInputValue("");
      inputRef.current?.blur();
    }
  };

  // Handle keyboard navigation for messages
  const handleMessageNavigation = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowUp" || e.key === "ArrowDown") {
      e.preventDefault();
      // Focus management for message navigation
      const messages =
        messagesContainerRef.current?.querySelectorAll('[role="article"]');
      if (messages && messages.length > 0) {
        const currentFocus = document.activeElement;
        const currentIndex = Array.from(messages).indexOf(
          currentFocus as Element
        );

        let newIndex = currentIndex;
        if (e.key === "ArrowUp") {
          newIndex = Math.max(0, currentIndex - 1);
        } else {
          newIndex = Math.min(messages.length - 1, currentIndex + 1);
        }

        (messages[newIndex] as HTMLElement).focus();
      }
    }
  };

  const handleInteractionClick = (messageId: string, action: string) => {
    websocketService.sendInteractionResponse(messageId, action);
  };

  const handleFeedback = (
    messageId: string,
    feedback: "helpful" | "not_helpful"
  ) => {
    websocketService.sendFeedback(messageId, feedback);
  };

  return (
    <div
      className={`h-screen flex flex-col bg-gray-50 ${
        preferences.highContrast ? "contrast-more" : ""
      } ${preferences.largeText ? "text-lg" : ""}`}
      onKeyDown={handleMessageNavigation}
    >
      {/* Skip Links */}
      <SkipLink href="#chat-messages">Skip to messages</SkipLink>
      <SkipLink href="#message-input">Skip to message input</SkipLink>

      {/* Screen Reader Announcements */}
      <ScreenReaderAnnouncement message={announcement} />

      {/* Live region for connection status */}
      <div aria-live="polite" className="sr-only">
        {isConnected ? "Connected to chat" : "Disconnected from chat"}
      </div>
      {/* Chat Header */}
      <header
        className={`bg-white border-b border-gray-200 shadow-sm ${
          isMobile ? "px-4 py-3" : "px-6 py-4"
        }`}
        role="banner"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => navigate("/dashboard")}
              className={`text-gray-600 hover:text-gray-900 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 rounded p-1 ${
                touchSupported ? "min-w-[44px] min-h-[44px]" : ""
              }`}
              aria-label="Back to dashboard"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 19l-7-7 7-7"
                />
              </svg>
            </button>
            <div className="min-w-0 flex-1">
              <h1
                className={`font-semibold text-gray-900 truncate ${
                  isMobile ? "text-base" : "text-lg"
                }`}
              >
                {selectedCharacter
                  ? `${selectedCharacter.name}'s Adventure`
                  : "Therapeutic Chat"}
              </h1>
              <div className="flex items-center space-x-2 mt-1">
                <div
                  className={`w-2 h-2 rounded-full transition-colors ${
                    isConnected ? "bg-green-500" : "bg-red-500"
                  }`}
                  aria-hidden="true"
                />
                <span className="text-sm text-gray-600 truncate">
                  {isConnected
                    ? "Connected"
                    : connectionError || "Disconnected"}
                </span>
                {isTyping && (
                  <span
                    className="text-sm text-blue-600 italic"
                    aria-live="polite"
                  >
                    Assistant is typing...
                  </span>
                )}
              </div>
            </div>
          </div>

          {!isMobile && (
            <div className="flex items-center space-x-3">
              <button
                className="p-2 text-gray-600 hover:text-gray-900 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
                onClick={() => navigate("/settings")}
                aria-label="Open settings"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Messages Area */}
      <main
        id="chat-messages"
        ref={messagesContainerRef}
        className={`flex-1 overflow-y-auto bg-gray-50 space-y-4 ${
          isMobile ? "p-4" : "p-6"
        }`}
        role="main"
        aria-label="Chat messages"
        tabIndex={-1}
      >
        {messageHistory.length === 0 ? (
          <div className={`text-center ${isMobile ? "py-8" : "py-12"}`}>
            <div
              className={`bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4 ${
                isMobile ? "w-12 h-12" : "w-16 h-16"
              }`}
            >
              <svg
                className={`text-blue-600 ${isMobile ? "w-6 h-6" : "w-8 h-8"}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
            </div>
            <h2
              className={`font-medium text-gray-900 mb-2 ${
                isMobile ? "text-base" : "text-lg"
              }`}
            >
              Welcome to your therapeutic adventure!
            </h2>
            <p
              className={`text-gray-600 mb-6 max-w-md mx-auto ${
                isMobile ? "text-sm px-4" : ""
              }`}
            >
              Start a conversation to begin your personalized therapeutic
              journey. Your responses will help guide the experience.
            </p>
            {!isConnected && (
              <div
                className={`bg-yellow-50 border border-yellow-200 rounded-lg p-4 max-w-md mx-auto ${
                  isMobile ? "mx-4" : ""
                }`}
              >
                <p
                  className="text-yellow-800 text-sm"
                  role="status"
                  aria-live="polite"
                >
                  Connecting to chat server...
                </p>
              </div>
            )}
          </div>
        ) : (
          messageHistory.map((message, index) => (
            <div
              key={message.id}
              role="article"
              aria-label={`Message ${index + 1} from ${message.type}`}
              tabIndex={0}
              className="focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
            >
              <ChatMessage
                message={message}
                onInteractionClick={handleInteractionClick}
                onFeedback={handleFeedback}
              />
            </div>
          ))
        )}

        {/* Typing Indicator */}
        <TypingIndicator isVisible={isTyping} />

        {/* Scroll anchor */}
        <div ref={messagesEndRef} aria-hidden="true" />
      </main>

      {/* Message Input */}
      <footer
        className={`bg-white border-t border-gray-200 shadow-lg ${
          isMobile ? "p-3" : "p-4"
        }`}
        role="contentinfo"
      >
        <div className={`${isMobile ? "" : "max-w-4xl mx-auto"}`}>
          <div
            className={`flex items-end ${isMobile ? "space-x-2" : "space-x-3"}`}
          >
            <div className="flex-1 relative">
              <label htmlFor="message-input" className="sr-only">
                Type your message
              </label>
              <input
                id="message-input"
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                onFocus={() => setIsInputFocused(true)}
                onBlur={() => setIsInputFocused(false)}
                placeholder={
                  isConnected ? "Type your message..." : "Connecting..."
                }
                className={`w-full border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 ${
                  isMobile ? "px-3 py-2 text-base" : "px-4 py-3"
                } ${
                  !isConnected
                    ? "bg-gray-100 border-gray-300 text-gray-500 cursor-not-allowed"
                    : "bg-white border-gray-300 text-gray-900"
                } ${isInputFocused ? "shadow-md" : "shadow-sm"} ${
                  touchSupported ? "min-h-[44px]" : ""
                }`}
                disabled={!isConnected}
                maxLength={1000}
                aria-describedby="message-help"
                autoComplete="off"
                autoCorrect="off"
                autoCapitalize="sentences"
                spellCheck="true"
              />
              {!isMobile && (
                <div
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-xs text-gray-400"
                  aria-hidden="true"
                >
                  {inputValue.length}/1000
                </div>
              )}
            </div>
            <button
              onClick={() => handleSendMessage(inputValue)}
              disabled={!isConnected || !inputValue.trim()}
              className={`rounded-lg font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                isMobile ? "px-4 py-2" : "px-6 py-3"
              } ${touchSupported ? "min-w-[44px] min-h-[44px]" : ""} ${
                isConnected && inputValue.trim()
                  ? "bg-blue-600 hover:bg-blue-700 text-white shadow-md hover:shadow-lg"
                  : "bg-gray-300 text-gray-500 cursor-not-allowed"
              }`}
              aria-label="Send message"
              type="submit"
            >
              {isMobile ? (
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                  />
                </svg>
              ) : (
                <>
                  <svg
                    className="w-5 h-5 inline mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                    />
                  </svg>
                  Send
                </>
              )}
            </button>
          </div>

          {/* Connection status and help text */}
          <div
            id="message-help"
            className={`mt-2 flex items-center justify-between ${
              isMobile ? "text-xs" : "text-xs"
            }`}
          >
            <div className="flex items-center space-x-4">
              {!isConnected && (
                <span
                  className="text-red-600 flex items-center space-x-1"
                  role="status"
                  aria-live="polite"
                >
                  <svg
                    className="w-3 h-3"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                    aria-hidden="true"
                  >
                    <path
                      fillRule="evenodd"
                      d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span>
                    {connectionError ||
                      "Disconnected - Attempting to reconnect..."}
                  </span>
                </span>
              )}
              {isConnected && (
                <span
                  className="text-green-600 flex items-center space-x-1"
                  role="status"
                >
                  <svg
                    className="w-3 h-3"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                    aria-hidden="true"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span>Connected securely</span>
                </span>
              )}
              {isMobile && (
                <span className="text-gray-500" aria-hidden="true">
                  {inputValue.length}/1000
                </span>
              )}
            </div>
            {!isMobile && (
              <span className="text-gray-500" aria-hidden="true">
                Press Enter to send • Escape to clear
              </span>
            )}
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Chat;
