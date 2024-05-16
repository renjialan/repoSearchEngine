document.getElementById('searchForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const repoUrl = document.getElementById('repoUrl').value;
    const searchQuery = document.getElementById('searchQuery').value;

    try {
        const searchResults = await searchGitHubRepo(repoUrl, searchQuery);
        displaySearchResults(searchResults);
    } catch (error) {
        console.error('Error searching GitHub repository:', error);
    }
});

async function searchGitHubRepo(repoUrl, searchQuery) {
    // Perform API call to backend server to search GitHub repository
    const response = await fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            repoUrl: repoUrl,
            searchQuery: searchQuery
        })
    });

    if (!response.ok) {
        throw new Error('Failed to search GitHub repository');
    }

    return response.json();
}

function displaySearchResults(results) {
    const searchResultsDiv = document.getElementById('searchResults');
    searchResultsDiv.innerHTML = '';

    if (results && results.length > 0) {
        const ul = document.createElement('ul');
        results.forEach(result => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = result.url;
            a.textContent = result.fileName;
            li.appendChild(a);
            ul.appendChild(li);
        });
        searchResultsDiv.appendChild(ul);
    } else {
        searchResultsDiv.textContent = 'No results found.';
    }
}


// new code gemni api

document.getElementById('searchForm').addEventListener('submit', async function (event) {
    event.preventDefault();
    const query = document.getElementById('searchInput').value;
    
    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        });
        const data = await response.json();
        // Display the generated text to the user
        document.getElementById('searchResult').textContent = data.generatedText;
    } catch (error) {
        console.error('Error searching GitHub repository:', error);
        document.getElementById('searchResult').textContent = 'Error searching GitHub repository';
    }
});