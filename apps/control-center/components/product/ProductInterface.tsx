"use client"

import { useState } from "react"
import { wsClient } from "@/lib/websocket"

export function ProductInterface() {
  const [searchQuery, setSearchQuery] = useState("")
  const [searchResults, setSearchResults] = useState<Array<{title: string, url: string, snippet: string}>>([])
  const [isSearching, setIsSearching] = useState(false)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchQuery.trim()) return

    setIsSearching(true)
    setSearchResults([])
    
    // Simulate search - this will generate Datadog monitoring data
    wsClient.send("product_action", JSON.stringify({
      action: "search",
      query: searchQuery,
      timestamp: new Date().toISOString()
    }))

    // Simulate search results with realistic delay
    setTimeout(() => {
      setSearchResults([
        {
          title: `${searchQuery} - Wikipedia`,
          url: `https://en.wikipedia.org/wiki/${encodeURIComponent(searchQuery)}`,
          snippet: `Learn about ${searchQuery}. Comprehensive information, history, and related topics.`
        },
        {
          title: `${searchQuery} | Official Site`,
          url: `https://www.${searchQuery.toLowerCase().replace(/\s+/g, '')}.com`,
          snippet: `Official website for ${searchQuery}. Get the latest updates, news, and resources.`
        },
        {
          title: `What is ${searchQuery}? - Complete Guide`,
          url: `https://example.com/guide/${encodeURIComponent(searchQuery)}`,
          snippet: `A complete guide to understanding ${searchQuery}. Everything you need to know in one place.`
        },
        {
          title: `${searchQuery} - News & Updates`,
          url: `https://news.example.com/${encodeURIComponent(searchQuery)}`,
          snippet: `Latest news and updates about ${searchQuery}. Stay informed with recent developments.`
        }
      ])
      setIsSearching(false)
    }, 800)
  }

  const handleAction = (actionType: string, data?: any) => {
    const actionData = {
      action: actionType,
      ...data,
      timestamp: new Date().toISOString()
    }
    wsClient.send("product_action", JSON.stringify(actionData))
  }

  return (
    <div className="flex flex-col min-h-full bg-white">
      {/* Top Navigation Bar - Google Style */}
      <div className="flex justify-end items-center px-6 py-4 gap-4 text-sm">
        <button 
          onClick={() => handleAction("browse_page", { page: "images" })}
          className="text-gray-700 hover:underline"
        >
          Images
        </button>
        <button 
          onClick={() => handleAction("browse_page", { page: "settings" })}
          className="text-gray-700 hover:underline"
        >
          Settings
        </button>
        <button 
          onClick={() => handleAction("view_profile")}
          className="w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center text-xs font-medium hover:bg-blue-600 transition-colors"
        >
          U
        </button>
      </div>

      {/* Main Search Area */}
      <div className="flex-1 flex flex-col items-center justify-start pt-32 px-4">
        {/* Logo */}
        <div className="mb-8">
          <h1 className="text-7xl font-normal tracking-tight" style={{ 
            fontFamily: 'system-ui, -apple-system, sans-serif',
            color: '#4285F4',
            letterSpacing: '-2px'
          }}>
            Goliath
          </h1>
        </div>

        {/* Search Box */}
        <div className="w-full max-w-2xl mb-6">
          <form onSubmit={handleSearch} className="relative">
            <div className="relative flex items-center">
              {/* Search Icon */}
              <svg 
                className="absolute left-4 w-5 h-5 text-gray-400" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              
              {/* Search Input */}
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder=""
                className="w-full pl-14 pr-14 py-4 text-base rounded-full border border-gray-300 shadow-sm hover:shadow-md focus:outline-none focus:shadow-lg focus:border-transparent transition-all"
                style={{ 
                  fontFamily: 'system-ui, -apple-system, sans-serif',
                  paddingLeft: '3.5rem',
                  paddingRight: '3.5rem'
                }}
              />
              
              {/* Microphone Icon */}
              <svg 
                className="absolute right-4 w-5 h-5 text-blue-500 cursor-pointer hover:text-blue-600" 
                fill="currentColor" 
                viewBox="0 0 24 24"
              >
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
              </svg>
            </div>
          </form>
        </div>

        {/* Search Buttons */}
        <div className="flex gap-3 mb-8">
          <button
            onClick={handleSearch}
            className="px-6 py-2 text-sm text-gray-700 bg-gray-50 border border-transparent rounded-md hover:border-gray-300 hover:shadow-sm transition-all"
            style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
          >
            {isSearching ? "Searching..." : "Goliath Search"}
          </button>
          <button
            onClick={() => handleAction("browse_page", { page: "lucky" })}
            className="px-6 py-2 text-sm text-gray-700 bg-gray-50 border border-transparent rounded-md hover:border-gray-300 hover:shadow-sm transition-all"
            style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
          >
            I'm Feeling Lucky
          </button>
        </div>

        {/* Hidden Action Buttons for Testing */}
        <div className="mt-auto mb-8 flex flex-wrap gap-2 justify-center opacity-40 hover:opacity-100 transition-opacity">
          <button
            onClick={() => handleAction("upload_file")}
            className="px-3 py-1 text-xs text-gray-600 bg-gray-100 rounded hover:bg-gray-200 transition-colors"
          >
            Upload
          </button>
          <button
            onClick={() => handleAction("trigger_error", { type: "high_error_rate" })}
            className="px-3 py-1 text-xs text-red-600 bg-red-50 rounded hover:bg-red-100 transition-colors"
          >
            Simulate Error
          </button>
          <button
            onClick={() => handleAction("generate_load", { intensity: 500 })}
            className="px-3 py-1 text-xs text-blue-600 bg-blue-50 rounded hover:bg-blue-100 transition-colors"
          >
            Generate Load
          </button>
        </div>
      </div>

      {/* Search Results */}
      {searchResults.length > 0 && (
        <div className="px-6 pb-8 max-w-3xl mx-auto w-full">
          <div className="text-sm text-gray-600 mb-4" style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}>
            About {searchResults.length} results (0.42 seconds)
          </div>
          <div className="space-y-6">
            {searchResults.map((result, idx) => (
              <div key={idx} className="hover:bg-gray-50 p-1 -m-1 rounded transition-colors">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs text-green-700" style={{ fontFamily: 'monospace' }}>
                    {result.url}
                  </span>
                </div>
                <a 
                  href="#" 
                  onClick={(e) => { e.preventDefault(); handleAction("browse_page", { page: result.url }); }}
                  className="text-xl text-blue-600 hover:underline block mb-1"
                  style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
                >
                  {result.title}
                </a>
                <p className="text-sm text-gray-600 leading-relaxed" style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}>
                  {result.snippet}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

