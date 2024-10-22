local cjson = require("cjson")
local http = require("socket.http")
local ltn12 = require("ltn12")

llm_set_mode("online")
llm_set_model("gpt-3.5-turbo-instruct")

-- Constants
local MAX_SEARCH_RESULTS = 5  -- Limit the number of search results to process

-- Helper function to handle JSON responses
local function handle_json_response(response)
    local success, result = pcall(cjson.decode, response)
    if success then
        return result
    else
        print("Error decoding JSON: " .. result)
        return nil
    end
end

-- Function to make an HTTP GET request
local function http_get(url)
    local response = {}
    local body, code, headers = http.request{
        url = url,
        method = "GET",
        sink = ltn12.sink.table(response)
    }
    if code ~= 200 then
        print("HTTP request failed with code: " .. code)
        return nil
    end
    return table.concat(response)
end

-- Function to perform search
local function perform_search(query)
    local encoded_query = query:gsub(" ", "%%20")
    local url = "https://ai-tools-dev.manufactured.com/searxng/search?q=" .. encoded_query .. "&format=json"
    local response = http_get(url)
    if not response then return nil end
    return handle_json_response(response)
end

-- Function to process content through LLM
local function process_with_llm(content)
    local prompt = "Summarize the following content in a concise manner:\n\n" .. content
    local response = llm_complete{prompt=prompt, max_tokens=150}
    return handle_json_response(response).text
end

-- Function to get embedding
local function get_embedding(text)
    local response = embed{text=text}
    local result = handle_json_response(response)
    if result and result.embedding then
        return result.embedding
    else
        print("Failed to get embedding for: " .. text)
        return nil
    end
end

-- Function to index all contents
local function index_contents(contents)
    local vectors = {}
    for i, content in ipairs(contents) do
        local embedding = get_embedding(content.summary)
        if embedding then
            vdb_add{key=i, vector=embedding}
            vectors[i] = embedding
        end
    end
    return vectors
end

-- Function to find best content using vector search
local function find_best_content(query, contents, vectors)
    local query_embedding = get_embedding(query)
    if not query_embedding then return nil end
    
    local search_result = handle_json_response(vdb_search{vector=query_embedding, k=1})
    if search_result and #search_result > 0 then
        local best_index = search_result[1].key
        return contents[best_index]
    end
    return nil
end

-- Main function to search and answer
local function search_and_answer(query)
    -- Perform search
    print("Searching for: " .. query)
    local search_results = perform_search(query)
    if not search_results or #search_results.results == 0 then
        print("No search results found")
        return
    end
    
    -- Limit the number of search results
    local limited_results = {}
    for i = 1, math.min(MAX_SEARCH_RESULTS, #search_results.results) do
        table.insert(limited_results, search_results.results[i])
    end
    
    -- Process contents through LLM
    local processed_contents = {}
    for i, result in ipairs(limited_results) do
        local summary = process_with_llm(result.content)
        table.insert(processed_contents, {summary = summary, url = result.url})
    end
    
    -- Index all contents
    local vectors = index_contents(processed_contents)
    
    -- Find best content using vector search
    local best_content = find_best_content(query, processed_contents, vectors)
    if not best_content then
        print("Failed to find relevant content")
        return
    end
    
    -- Generate final answer
    local answer_prompt = string.format(
        "Based on the following information, answer the question '%s':\n\n%s",
        query,
        best_content.summary
    )
    local answer = process_with_llm(answer_prompt)
    
    -- Output answer with citation
    print("Answer:")
    print(answer)
    print("\nSource: " .. best_content.url)
end

-- Set up embedding model
local set_type_result = handle_json_response(set_embedding_type{embedding_type="text"})
if set_type_result and set_type_result.status == "success" then
    print("Embedding type set successfully")
else
    print("Failed to set embedding type")
    return
end

local set_model_result = handle_json_response(set_model{model_name="BAAI/bge-small-en-v1.5"})
if set_model_result and set_model_result.status == "success" then
    print("Model set successfully")
else
    print("Failed to set model")
    return
end

-- Create a vector index for similarity search
local create_index_result = handle_json_response(vdb_create_index{ndim=384, metric='cos', dtype='f32'})
if create_index_result and create_index_result.status == "success" then
    print("Vector index created successfully")
else
    print("Failed to create vector index")
    return
end

-- Example usage
search_and_answer("What is quantum physics?")