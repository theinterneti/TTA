import React, { useState, useEffect, useRef } from "react";
import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../../store/store";
import {
  addMessage,
  setConnectionStatus,
  setTypingStatus,
} from "../../store/slices/chatSlice";
import { selectCharacter } from "../../store/slices/characterSlice";
import ChatMessage from "../Chat/ChatMessage";
import TypingIndicator from "../Chat/TypingIndicator";
import ConversationProgress from "./ConversationProgress";
import ConversationCompletion from "./ConversationCompletion";
import TherapeuticConversationUI from "./TherapeuticConversationUI";
import conversationalWebSocketService from "../../services/conversationalWebSocketService";

interface ConversationMessage {
  id: string;
  type: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
  metadata?: {
    stage?: string;
    prompt_id?: string;
    context_text?: string;
    follow_up_prompts?: string[];
    progress?: {
      current_stage: string;
      progress_percentage: number;
      completed_stages: string[];
    };
    character_preview?: any;
    crisis_level?: string;
    resources?: Array<{ name: string; contact: string }>;
    // For ChatMessage compatibility
    therapeutic_technique?: string;
    safety_level?: "crisis" | "safe" | "caution";
    safety?: { crisis?: boolean };
    interactive_elements?: any;
  };
}

interface ConversationalCharacterCreationProps {
  onClose: () => void;
  onSuccess?: (characterId: string) => void;
  onNavigateToCharacter?: (characterId: string) => void;
  onNavigateToChat?: (characterId: string) => void;
}

const ConversationalCharacterCreation: React.FC<
  ConversationalCharacterCreationProps
> = ({ onClose, onSuccess, onNavigateToCharacter, onNavigateToChat }) => {
  const dispatch = useDispatch();
  const { profile } = useSelector((state: RootState) => state.player);
  const { isTyping } = useSelector((state: RootState) => state.chat);

  // Component state
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [isConversationActive, setIsConversationActive] = useState(false);
  const [conversationProgress, setConversationProgress] = useState({
    current_stage: "welcome",
    progress_percentage: 0,
    completed_stages: [] as string[],
  });
  const [isCompleted, setIsCompleted] = useState(false);
  const [characterPreview, setCharacterPreview] = useState<any>(null);
  const [createdCharacterId, setCreatedCharacterId] = useState<string | null>(
    null
  );

  // WebSocket and input state
  const [inputValue, setInputValue] = useState("");
  const [socket, setSocket] = useState<WebSocket | null>(null);

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Connect to WebSocket on component mount
  useEffect(() => {
    if (profile?.player_id) {
      connectToConversationalWebSocket();
    }
    return () => {
      conversationalWebSocketService.disconnect();
    };
  }, [profile?.player_id]);

  const connectToConversationalWebSocket = async () => {
    if (!profile?.player_id) {
      setConnectionError("Player ID not found");
      return;
    }

    try {
      setIsConnected(false);
      setConnectionError(null);

      await conversationalWebSocketService.connect(profile.player_id);

      setIsConnected(true);
      setConversationId(conversationalWebSocketService.getConversationId());
    } catch (error) {
      console.error("Failed to connect to conversational WebSocket:", error);
      setConnectionError("Failed to connect. Please try again.");
      setIsConnected(false);
    }
  };

  const startConversation = (websocket: WebSocket) => {
    const startMessage = {
      type: "start_conversation",
      player_id: profile?.player_id,
      metadata: {
        source: "character_creation_ui",
      },
    };

    websocket.send(JSON.stringify(startMessage));
  };

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case "conversation_started":
        setConversationId(data.conversation_id);
        setIsConversationActive(true);
        break;

      case "assistant_message":
        const assistantMessage: ConversationMessage = {
          id: data.message_id || `assistant_${Date.now()}`,
          type: "assistant",
          content: data.content,
          timestamp: data.timestamp || new Date().toISOString(),
          metadata: {
            stage: data.stage,
            prompt_id: data.prompt_id,
            context_text: data.context_text,
            follow_up_prompts: data.follow_up_prompts,
          },
        };
        setMessages((prev) => [...prev, assistantMessage]);
        dispatch(setTypingStatus(false));
        break;

      case "progress_update":
        setConversationProgress(data.progress);
        break;

      case "conversation_completed":
        const completionMessage: ConversationMessage = {
          id: `completion_${Date.now()}`,
          type: "system",
          content:
            "Congratulations! Your therapeutic companion has been created successfully.",
          timestamp: new Date().toISOString(),
          metadata: {
            character_preview: data.character_preview,
          },
        };
        setMessages((prev) => [...prev, completionMessage]);
        setIsConversationActive(false);

        // Call success callback with character ID
        if (onSuccess && data.character_preview?.character_id) {
          setTimeout(
            () => onSuccess(data.character_preview.character_id),
            2000
          );
        }
        break;

      case "validation_error":
        const errorMessage: ConversationMessage = {
          id: `error_${Date.now()}`,
          type: "system",
          content: data.error_message,
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, errorMessage]);
        break;

      case "crisis_detected":
        const crisisMessage: ConversationMessage = {
          id: `crisis_${Date.now()}`,
          type: "system",
          content: data.support_message,
          timestamp: new Date().toISOString(),
          metadata: {
            crisis_level: data.crisis_level,
            resources: data.resources,
          },
        };
        setMessages((prev) => [...prev, crisisMessage]);
        break;

      case "error":
        setConnectionError(data.error_message);
        break;

      default:
        console.log("Unknown message type:", data.type);
    }
  };

  const handleSendMessage = () => {
    if (!inputValue.trim() || !socket || !isConnected || !conversationId)
      return;

    // Add user message to UI immediately
    const userMessage: ConversationMessage = {
      id: `user_${Date.now()}`,
      type: "user",
      content: inputValue.trim(),
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    // Send to server
    const responseMessage = {
      type: "user_response",
      conversation_id: conversationId,
      content: inputValue.trim(),
      timestamp: new Date().toISOString(),
    };

    socket.send(JSON.stringify(responseMessage));

    // Show typing indicator
    dispatch(setTypingStatus(true));

    // Clear input
    setInputValue("");
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handlePauseConversation = () => {
    if (socket && conversationId) {
      const pauseMessage = {
        type: "pause_conversation",
        conversation_id: conversationId,
      };
      socket.send(JSON.stringify(pauseMessage));
    }
  };

  const handleAbandonConversation = () => {
    if (socket && conversationId) {
      const abandonMessage = {
        type: "abandon_conversation",
        conversation_id: conversationId,
      };
      socket.send(JSON.stringify(abandonMessage));
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl h-5/6 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <h2 className="text-xl font-semibold text-gray-900">
              Create Your Therapeutic Companion
            </h2>
            <div
              className={`w-2 h-2 rounded-full ${
                isConnected ? "bg-green-500" : "bg-red-500"
              }`}
            />
            <span className="text-sm text-gray-600">
              {isConnected ? "Connected" : connectionError || "Disconnected"}
            </span>
          </div>

          <div className="flex items-center space-x-2">
            {isConversationActive && (
              <button
                onClick={handlePauseConversation}
                className="px-3 py-1 text-sm bg-yellow-100 text-yellow-800 rounded-md hover:bg-yellow-200 transition-colors"
              >
                Pause
              </button>
            )}
            <button
              onClick={handleAbandonConversation}
              className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <ConversationProgress progress={conversationProgress} />

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {!isConnected && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">
                Connecting to your therapeutic companion creator...
              </p>
            </div>
          )}

          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message}
              onInteractionClick={() => {}} // No interactions needed for character creation
              onFeedback={() => {}} // No feedback needed for character creation
            />
          ))}

          <TypingIndicator isVisible={isTyping} />
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        {isConnected && isConversationActive && (
          <div className="border-t border-gray-200 p-4">
            <div className="flex space-x-3">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Share your thoughts..."
                className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={!isConnected || !isConversationActive}
              />
              <button
                onClick={handleSendMessage}
                disabled={
                  !inputValue.trim() || !isConnected || !isConversationActive
                }
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                Send
              </button>
            </div>

            <div className="mt-2 text-xs text-gray-500 text-center">
              This is a safe space. Share as much or as little as feels
              comfortable.
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ConversationalCharacterCreation;
