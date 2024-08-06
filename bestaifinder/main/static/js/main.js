// Function to generate a slug from a tag, specifically for creating tag links
function generateSlug(tag) {
  return tag.toLowerCase().replace(/[^a-z0-9]+/g, '-');
}

// Function to handle click events on tags
function handleTagClick(tag) {
  var tagSlug = generateSlug(tag);
  window.location.href = "/tags/" + tagSlug;
}

// Get all tag elements
var tags = document.querySelectorAll(".tag");

// Attach click event listeners to each tag
tags.forEach(function(tagElement) {
  tagElement.addEventListener("click", function() {
      var tag = tagElement.innerText;
      handleTagClick(tag);
  });
});



// Function to copy page link for sharing tool
function copyPageLink() {
var copyText = window.location.href;

// Create a temporary element (textarea) to hold the text
var tempInput = document.createElement("textarea");
tempInput.value = copyText;

// Append the textarea to the body
document.body.appendChild(tempInput);

// Select the text in the textarea
tempInput.select();
tempInput.setSelectionRange(0, 99999); // For mobile devices

try {
  // Copy the text inside the textarea
  document.execCommand("copy");
  // Remove the temporary textarea
  document.body.removeChild(tempInput);
  // Alert the copied text
  alert("Link copied to clipboard!");
} catch (err) {
  console.error('Unable to copy text: ', err);
  alert("Failed to copy link. Please try again.");
}
}




// When the user scrolls down 20px from the top of the document, show the button
window.onscroll = function() {scrollFunction()};

function scrollFunction() {
  if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
      document.getElementById("myBtn").style.display = "block";
  } else {
      document.getElementById("myBtn").style.display = "none";
  }
}

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
  document.body.scrollTop = 0; // For Safari
  document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}


// Function to open the tool preview
function openTool(url, toolName, toolSlug, visitToolLink) {
  $('#loader').show();
  $('#toolIframe').hide();
  $('#error').hide();

  document.getElementById('toolModalLabel').innerText = toolName;
  document.getElementById('toolIframe').src = url;

  // Show the modal
  $('#toolModal').modal('show');

  // Set Learn More link before iframe loads
  if (toolSlug !== null) {
    var learnMoreLink = $('a[href*="' + toolSlug + '"]');
    if (learnMoreLink.length > 0) {
      $('#learnMoreLink').attr('href', learnMoreLink.attr('href'));
      $('#learnMoreLink').show();
    } else {
      $('#learnMoreLink').hide();
    }
  } else {
    $('#learnMoreLink').hide();
  }

  // Handle iframe load event
  document.getElementById('toolIframe').onload = function() {
    $('#loader').hide();
    $('#toolIframe').show();
  };

  // Handle iframe error event
  document.getElementById('toolIframe').onerror = function() {
    $('#loader').hide();
    $('#errorMessage').text(toolName + ' refused to connect.');
    $('#error').show();
  };

  // Set Open in New Tab link
  document.getElementById('openInNewTabFooterBtn').onclick = function() {
    openInNewTab(visitToolLink);
  };
}

// Function to open URL in a new tab with confirmation
function openInNewTab(url) {
  if (confirm('You are leaving AI Finder Guru. Would you like to proceed?')) {
    var win = window.open(url, '_blank');
    if (win) {
      win.focus();
    } else {
      alert('Please allow popups for this site to open in a new tab.');
    }
  }
}

// Event handler for opening Learn More link in the same tab
document.getElementById('learnMoreLink').onclick = function(event) {
  event.preventDefault(); // Prevent default link behavior
  window.location.href = this.getAttribute('href'); // Open in the same tab
};

// Event handler for error button
document.getElementById('openInNewTabBtnError').onclick = function() {
  openInNewTab(document.getElementById('toolIframe').src);
};



// Script for preventing maximum page number entry in 'jump to page form'
document.addEventListener('DOMContentLoaded', function() {
  const jumpToPageForm = document.getElementById('jump-to-page-form');
  if (jumpToPageForm) {
      jumpToPageForm.addEventListener('submit', function(event) {
          const pageNumberInput = document.getElementById('page-number-input');
          const pageNumber = parseInt(pageNumberInput.value, 10);
          const maxPages = parseInt(jumpToPageForm.getAttribute('data-max-pages'), 10);
          if (pageNumber < 1 || pageNumber > maxPages) {
              event.preventDefault();
              alert(`Please enter a number between 1 and ${maxPages}`);
          } else {
              this.action = `?page=${pageNumber}#all-tools`;
          }
      });
  }
});



// script to validate AI Exact ID input at the search form
document.addEventListener('DOMContentLoaded', function() {
const aiExactIdForm = document.getElementById('ai-exact-id-form');
if (aiExactIdForm) {
    aiExactIdForm.addEventListener('submit', function(event) {
        const aiExactIdInput = document.getElementById('ai-exact-id-input');
        const aiExactId = parseInt(aiExactIdInput.value, 10);
        const maxToolsCount = parseInt('{{ all_ai_tools_count }}', 10); // Replace with actual count from Django context
        
        console.log(`AI Exact ID entered: ${aiExactId}`);
        console.log(`Max tools count: ${maxToolsCount}`);

        if (isNaN(aiExactId) || aiExactId < 1 || aiExactId > maxToolsCount) {
            event.preventDefault();
            alert(`Please enter a number between 1 and ${maxToolsCount}`);
        }
    });
} else {
    console.error('Form element with ID "ai-exact-id-form" not found.');
}

});




// Function to show QR code modal
function showQRCodeModal(toolLink) {
const modal = document.getElementById('qrCodeModal');
const spinner = modal.querySelector('.spinner-border');
const qrCodeContent = document.getElementById('qrCodeContent');

// Show loading spinner
spinner.style.display = 'inline-block';
qrCodeContent.innerHTML = ''; // Clear previous content

// Generate QR code dynamically
const qrCodeImage = new Image();
qrCodeImage.src = `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(toolLink)}`;
qrCodeImage.onload = function() {
  qrCodeContent.appendChild(qrCodeImage);
  spinner.style.display = 'none'; // Hide spinner
};

// Show modal
$(modal).modal('show');
}

// Function to copy and share link
function copyPageLink() {
    const pageUrl = window.location.href;
    navigator.clipboard.writeText(pageUrl).then(() => {
        alert('Link copied to clipboard!');
    });
}

function shareTo(platform) {
    const pageUrl = encodeURIComponent(window.location.href);
    let shareUrl = '';
    switch (platform) {
        case 'whatsapp':
            shareUrl = `https://wa.me/?text=${pageUrl}`;
            break;
        case 'facebook':
            shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${pageUrl}`;
            break;
        case 'x':
            shareUrl = `https://twitter.com/intent/tweet?url=${pageUrl}`;
            break;
        case 'linkedin':
            shareUrl = `https://www.linkedin.com/shareArticle?mini=true&url=${pageUrl}`;
            break;
    }
    window.open(shareUrl, '_blank');
}

function toggleDropdown() {
    const dropdownMenu = document.getElementById('dropdownMenu');
    const buttonRect = document.getElementById('dropdownMenuButton').getBoundingClientRect();
    const viewportHeight = window.innerHeight;

    if (buttonRect.bottom + dropdownMenu.offsetHeight > viewportHeight) {
        dropdownMenu.style.top = `${-dropdownMenu.offsetHeight}px`;
    } else {
        dropdownMenu.style.top = `${buttonRect.height}px`;
    }

    dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
}

// Close the dropdown if the user clicks outside of it
window.onclick = function(event) {
    if (!event.target.matches('.dropdown-toggle')) {
        const dropdowns = document.getElementsByClassName('dropdown-menu');
        for (let i = 0; i < dropdowns.length; i++) {
            const openDropdown = dropdowns[i];
            if (openDropdown.style.display === 'block') {
                openDropdown.style.display = 'none';
            }
        }
    }
}
