"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { ArrowUpIcon, Paperclip } from "lucide-react";
import MessageBubble from "./MessageBubble.tsx";
import SourceCard from "./SourceCard.tsx";
import PixelBlast from "./PixelBlast";
import StaggeredMenu from "./StaggeredMenu";
import BlurText from "./BlurText";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Array<{ title: string; url: string; relevance: number }>;
  suggestions?: string[];
  relatedQueries?: string[];
  usedWebSearch?: boolean;
  lastUserQuery?: string;
  timestamp: Date;
}

interface UseAutoResizeTextareaProps {
  minHeight: number;
  maxHeight?: number;
}

function useAutoResizeTextarea({
  minHeight,
  maxHeight,
}: UseAutoResizeTextareaProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustHeight = useCallback(
    (reset?: boolean) => {
      const textarea = textareaRef.current;
      if (!textarea) return;

      if (reset) {
        textarea.style.height = `${minHeight}px`;
        return;
      }

      textarea.style.height = `${minHeight}px`;
      const newHeight = Math.max(
        minHeight,
        Math.min(
          textarea.scrollHeight,
          maxHeight ?? Number.POSITIVE_INFINITY
        )
      );
      textarea.style.height = `${newHeight}px`;
    },
    [minHeight, maxHeight]
  );

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = `${minHeight}px`;
    }
  }, [minHeight]);

  useEffect(() => {
    const handleResize = () => adjustHeight();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [adjustHeight]);

  return { textareaRef, adjustHeight };
}

const SUGGESTED_QUESTIONS = [
  "How do I create a campaign?",
  "What is the audience manager?",
  "How do I send my first message?",
  "How do I set up SMS Magic?",
];

// API URL - uses environment variable in production, localhost in development
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [value, setValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [searchingWeb, setSearchingWeb] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [conversations, setConversations] = useState<Array<{ id: string; title: string; messages: Message[] }>>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string>('default');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { textareaRef, adjustHeight } = useAutoResizeTextarea({
    minHeight: 60,
    maxHeight: 200,
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (messageText?: string, diveDeeper: boolean = false) => {
    const textToSend = messageText || value;
    if (!textToSend.trim() || isLoading) return;

    const userMessage: Message = {
      role: "user",
      content: textToSend,
      timestamp: new Date(),
    };

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    
    // Save or update conversation
    if (messages.length === 0) {
      const newConv = {
        id: currentConversationId,
        title: textToSend.slice(0, 50) + (textToSend.length > 50 ? '...' : ''),
        messages: newMessages
      };
      setConversations(prev => [...prev, newConv]);
    } else {
      // Update existing conversation
      setConversations(prev => 
        prev.map(conv => 
          conv.id === currentConversationId 
            ? { ...conv, messages: newMessages }
            : conv
        )
      );
    }
    setValue("");
    adjustHeight(true);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          message: textToSend,
          dive_deeper: diveDeeper 
        }),
      });

      const data = await response.json();

      const assistantMessage: Message = {
        role: "assistant",
        content: data.response,
        sources: data.sources,
        suggestions: data.suggestions,
        relatedQueries: data.related_queries || [],
        usedWebSearch: data.used_web_search,
        lastUserQuery: textToSend,
        timestamp: new Date(),
      };

      setMessages((prev) => {
        const updatedMessages = [...prev, assistantMessage];
        // Update conversation with assistant response
        setConversations(convs => 
          convs.map(conv => 
            conv.id === currentConversationId 
              ? { ...conv, messages: updatedMessages }
              : conv
          )
        );
        return updatedMessages;
      });
    } catch (error) {
      console.error("Error:", error);
      const errorMessage: Message = {
        role: "assistant",
        content:
          "Sorry, I encountered an error. Please make sure the backend is running.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDiveDeeper = async (query: string) => {
    // Show initial comprehensive searching message
    const searchingMessage: Message = {
      role: "assistant",
      content: "Hold on! Let me go through additional relevant documents and search the web for comprehensive information...",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, searchingMessage]);
    setIsLoading(true);
    setSearchingWeb(true);
    
    // Update conversation
    setConversations(prev => 
      prev.map(conv => 
        conv.id === currentConversationId 
          ? { ...conv, messages: [...conv.messages, searchingMessage] }
          : conv
      )
    );

    try {
      // Call dive deeper endpoint (searches docs + web)
      const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          message: query,
          dive_deeper: true 
        }),
      });

      const data = await response.json();
      
      // Show final comprehensive response
      const assistantMessage: Message = {
        role: "assistant",
        content: data.response,
        sources: data.sources,
        suggestions: data.suggestions,
        relatedQueries: data.related_queries || [],
        usedWebSearch: true,  // Always true for dive deeper
        lastUserQuery: query,
        timestamp: new Date(),
      };

      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = assistantMessage;
        
        // Update conversation
        setConversations(convs => 
          convs.map(conv => 
            conv.id === currentConversationId 
              ? { ...conv, messages: updated }
              : conv
          )
        );
        return updated;
      });
      
    } catch (error) {
      console.error("Error:", error);
      const errorMessage: Message = {
        role: "assistant",
        content: "Sorry, I encountered an error during the deep search. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = errorMessage;
        return updated;
      });
    } finally {
      setIsLoading(false);
      setSearchingWeb(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (value.trim()) {
        sendMessage();
      }
    }
  };

  const handleSuggestedQuestion = (question: string) => {
    setValue(question);
    sendMessage(question);
  };

  const handleConversationClick = (convId: string) => {
    const conv = conversations.find(c => c.id === convId);
    if (conv) {
      setCurrentConversationId(convId);
      setMessages(conv.messages);
    }
  };

  const handleNewChat = () => {
    const newId = `conv-${Date.now()}`;
    setCurrentConversationId(newId);
    setMessages([]);
  };

  const conversationItems = [
    {
      label: '+ New Chat',
      ariaLabel: 'Start a new conversation',
      link: '#new',
      onClick: handleNewChat
    },
    ...conversations.map(conv => ({
      label: conv.title,
      ariaLabel: `Open conversation: ${conv.title}`,
      link: `#${conv.id}`,
      onClick: () => handleConversationClick(conv.id)
    }))
  ];

  return (
    <>
      <StaggeredMenu
        position="right"
        colors={['#B19EEF', '#5227FF']}
        items={conversationItems}
        displaySocials={false}
        displayItemNumbering={false}
        menuButtonColor="#fff"
        openMenuButtonColor="#000"
        changeMenuColorOnOpen={true}
        accentColor="#8B5CF6"
        isFixed={true}
        onMenuOpen={() => setMenuOpen(true)}
        onMenuClose={() => setMenuOpen(false)}
      />
      <div 
        className={`relative w-full h-screen overflow-hidden bg-neutral-950 transition-all duration-500 ${
          menuOpen ? 'mr-[25vw]' : 'mr-0'
        }`}
        style={{ maxWidth: menuOpen ? 'calc(100vw - min(320px, 25vw))' : '100vw' }}
      >
        <div className="absolute inset-0 z-0 w-full h-full" style={{ willChange: 'auto' }}>
        <PixelBlast
          key="pixel-blast-bg"
          variant="square"
          pixelSize={4}
          color="#B19EEF"
          patternScale={2}
          patternDensity={1}
          pixelSizeJitter={0}
          enableRipples={true}
          rippleSpeed={0.3}
          rippleThickness={0.1}
          rippleIntensityScale={1}
          liquid={false}
          liquidStrength={0.1}
          liquidRadius={1}
          liquidWobbleSpeed={4.5}
          speed={0.5}
          edgeFade={0.25}
          noiseAmount={0}
          transparent={true}
        />
      </div>
      {/* Logo and Branding - Fixed in upper left */}
      <div className="absolute top-8 left-8 z-20 flex items-center gap-4">
        <img 
          src="/conversive-logo.png" 
          alt="Conversive Logo" 
          className="h-12 w-auto"
        />
        <div className="flex flex-col">
          <h2 className="text-2xl font-bold text-white leading-tight">
            Convie
          </h2>
          <p className="text-xs text-neutral-400">
            Support by Conversive
          </p>
        </div>
      </div>

      <div className="flex flex-col items-center w-full h-screen mx-auto p-4 space-y-8 relative z-10">
        {messages.length === 0 ? (
          <>
            <div className="flex-1 flex flex-col items-center justify-center w-full max-w-4xl">
              <BlurText
                text="What can I help you with?"
                delay={150}
                animateBy="words"
                direction="bottom"
                className="text-5xl font-bold text-white mb-12"
              />

              {/* Input Box */}
              <div className="w-full mb-8">
                <div className="relative bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl p-[2px]">
                  <div className="bg-neutral-900 rounded-2xl">
                    <textarea
                      ref={textareaRef}
                      value={value}
                      onChange={(e) => {
                        setValue(e.target.value);
                        adjustHeight();
                      }}
                      onKeyDown={handleKeyDown}
                      placeholder="Ask a question about Conversive..."
                      className="w-full px-4 py-3 resize-none bg-transparent border-none text-white text-sm focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 placeholder:text-neutral-500 placeholder:text-sm min-h-[60px] rounded-2xl"
                      style={{ overflow: "hidden" }}
                    />
                    <div className="flex items-center justify-between px-3 pb-3">
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          className="group p-2 hover:bg-neutral-800 rounded-lg transition-colors flex items-center gap-1"
                        >
                          <Paperclip className="w-4 h-4 text-white" />
                          <span className="text-xs text-zinc-400 hidden group-hover:inline transition-opacity">
                            Attach
                          </span>
                        </button>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => sendMessage()}
                          className={`px-1.5 py-1.5 rounded-lg text-sm transition-colors border border-zinc-700 hover:border-zinc-600 hover:bg-zinc-800 flex items-center justify-between gap-1 ${
                            value.trim()
                              ? "bg-white text-black"
                              : "text-zinc-400"
                          }`}
                        >
                          <ArrowUpIcon
                            className={`w-4 h-4 ${
                              value.trim() ? "text-black" : "text-zinc-400"
                            }`}
                          />
                          <span className="sr-only">Send</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Suggested Questions */}
              <div className="flex items-center justify-center gap-3 flex-wrap">
                {SUGGESTED_QUESTIONS.map((question, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSuggestedQuestion(question)}
                    className="px-4 py-2 bg-neutral-900 hover:bg-neutral-800 rounded-full border border-neutral-800 text-neutral-400 hover:text-white transition-colors text-xs"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          </>
        ) : (
          <>
            {/* Messages View */}
            <div className="flex-1 overflow-y-auto w-full max-w-4xl space-y-4 pt-8 px-4 scrollbar-hide">
              {messages.map((message, index) => (
                <div key={index}>
                  <MessageBubble message={message} />
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-2 space-y-2">
                      {message.sources.map((source, idx) => (
                        <SourceCard key={idx} source={source} />
                      ))}
                    </div>
                  )}
                  {message.role === "assistant" && (
                    <div className="mt-3 space-y-3">
                      {/* Dive Deeper Button - Only show if not already used web search */}
                      {!message.usedWebSearch && message.lastUserQuery && (
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleDiveDeeper(message.lastUserQuery!)}
                            className="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 rounded-full text-white font-medium transition-all text-xs flex items-center gap-2"
                          >
                            <span>🔍</span>
                            Dive Deeper
                          </button>
                        </div>
                      )}

                      {/* Related Queries Section */}
                      {message.relatedQueries && message.relatedQueries.length > 0 && (
                        <div className="space-y-2">
                          <p className="text-xs text-neutral-500 font-medium">Related:</p>
                          <div className="flex flex-wrap gap-2">
                            {message.relatedQueries.map((query, idx) => (
                              <button
                                key={idx}
                                onClick={() => handleSuggestedQuestion(query)}
                                className="px-4 py-2 bg-neutral-900 hover:bg-neutral-800 rounded-full border border-neutral-800 text-neutral-400 hover:text-white transition-colors text-xs"
                              >
                                {query}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* General Suggestions */}
                      {message.suggestions && message.suggestions.length > 0 && (
                        <div className="space-y-2">
                          <p className="text-xs text-neutral-500 font-medium">You might also like:</p>
                          <div className="flex flex-wrap gap-2">
                            {message.suggestions.map((suggestion, idx) => (
                              <button
                                key={idx}
                                onClick={() => handleSuggestedQuestion(suggestion)}
                                className="px-4 py-2 bg-neutral-900 hover:bg-neutral-800 rounded-full border border-neutral-800 text-neutral-400 hover:text-white transition-colors text-xs"
                              >
                                {suggestion}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}

              {isLoading && (
                <div className="space-y-2">
                  {searchingWeb && (
                    <div className="text-sm text-purple-400 italic">
                      I couldn't find enough information in my stored data. Let me search the web for you...
                    </div>
                  )}
                  <div className="flex items-center space-x-2 text-white/60">
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }} />
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input at bottom when chatting */}
            <div className="w-full max-w-4xl pb-4 px-4">
              <div className="relative bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl p-[2px]">
                <div className="bg-neutral-900 rounded-2xl">
                  <textarea
                    ref={textareaRef}
                    value={value}
                    onChange={(e) => {
                      setValue(e.target.value);
                      adjustHeight();
                    }}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask a follow-up question..."
                    className="w-full px-4 py-3 resize-none bg-transparent border-none text-white text-sm focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 placeholder:text-neutral-500 placeholder:text-sm min-h-[60px] rounded-2xl"
                    style={{ overflow: "hidden" }}
                  />
                  <div className="flex items-center justify-between px-3 pb-3">
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        className="group p-2 hover:bg-neutral-800 rounded-lg transition-colors flex items-center gap-1"
                      >
                        <Paperclip className="w-4 h-4 text-white" />
                        <span className="text-xs text-zinc-400 hidden group-hover:inline transition-opacity">
                          Attach
                        </span>
                      </button>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => sendMessage()}
                        disabled={isLoading || !value.trim()}
                        className={`px-1.5 py-1.5 rounded-lg text-sm transition-colors border border-zinc-700 hover:border-zinc-600 hover:bg-zinc-800 flex items-center justify-between gap-1 ${
                          value.trim() ? "bg-white text-black" : "text-zinc-400"
                        }`}
                      >
                        <ArrowUpIcon
                          className={`w-4 h-4 ${
                            value.trim() ? "text-black" : "text-zinc-400"
                          }`}
                        />
                        <span className="sr-only">Send</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
    </>
  );
}
