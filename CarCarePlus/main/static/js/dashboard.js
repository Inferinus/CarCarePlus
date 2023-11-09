document.addEventListener('DOMContentLoaded', function() {
  // Fetch vehicles and attach them to the DOM
  fetchVehiclesAndDisplay();

  // Logout confirmation
  const logoutLink = document.querySelector('.logout-link');
  if (logoutLink) {
    logoutLink.addEventListener('click', function(event) {
      const confirmation = confirm('Are you sure you want to logout?');
      if (!confirmation) {
        event.preventDefault();
      }
    });
  }

  // Modal functionality
  var modal = document.getElementById("maintenanceModal");
  var span = document.getElementsByClassName("close")[0];

  // When the user clicks on <span> (x), close the modal
  span.onclick = function() {
    modal.style.display = "none";
  }

  // When the user clicks anywhere outside of the modal, close it
  window.onclick = function(event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  }
});

// This function should be triggered by the "Load Image" button for each vehicle.
function fetchAndDisplayVehicleImage(vin) {
  // Construct the endpoint for your API call using the VIN.
  const imageUrl = `/api/vehicle_image/${vin}`;

  // Fetch the image from your API.
  fetch(imageUrl)
    .then(response => {
      // Check if the response is ok (status code 200-299).
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.blob(); // Or `response.json()` if your server returns JSON data.
    })
    .then(blob => {
      // Create a local URL for the blob object.
      const imageSrc = URL.createObjectURL(blob);

      // Find the image element for this VIN and set the src to the blob URL.
      const imageElement = document.getElementById(`vehicleImage_${vin}`);
      imageElement.src = imageSrc;
    })
    .catch(error => {
      console.error('Error fetching vehicle image:', error);
      
      // Optionally, set a default image if the fetch fails.
      const defaultImagePath = document.body.getAttribute('data-default-image-path');
      const imageElement = document.getElementById(`vehicleImage_${vin}`);
      imageElement.src = defaultImagePath;
    });
}


/*function displayVehicleImage(vin) {
  var imgElement = document.getElementById('vehicle-image-' + vin);
  var defaultImagePath = document.body.getAttribute('data-default-image-path');

  console.log(`Fetching image for VIN: ${vin}`);
  fetch(`/vehicle_image/${vin}`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok.');
      }
      return response.blob();
    })
    .then(blob => {
      console.log(`Received blob for VIN: ${vin}, Blob size: ${blob.size}, Blob type: ${blob.type}`);
      if (blob.size > 0 && blob.type.startsWith('image/')) {
        const imageURL = URL.createObjectURL(blob);
        imgElement.src = imageURL;
      } else {
        console.warn(`No valid image received for VIN: ${vin}, setting default image.`);
        imgElement.src = defaultImagePath;
      }
    })
    .catch(error => {
      console.error(`Error fetching vehicle image for VIN: ${vin}`, error);
      imgElement.src = defaultImagePath;
    });
}*/

function displayVehicleImage(vin) {
  // Fetch the image data from the server for a given VIN
  fetch(`/vehicle_image/${vin}`)
    .then(response => response.json())
    .then(json => {
      console.log(json); // Log the JSON to inspect what's being received
      // If the JSON has an 'image_url' key, display the image
      if (json.image_url) {
        const imgElement = document.getElementById('vehicle-image-' + vin);
        imgElement.src = json.image_url;
        imgElement.alt = 'Vehicle Image';
      } else if (json.error) {
        // If there's an error in the JSON, log it and set a default image
        console.error('Error fetching image:', json.error);
        setDefaultImage(vin);
      } else {
        // If the JSON does not have the expected keys, log and set a default image
        console.error('Unexpected JSON structure:', json);
        setDefaultImage(vin);
      }
    })
    .catch(error => {
      // If there's an error in fetching, log it and set a default image
      console.error('Fetch error:', error);
      setDefaultImage(vin);
    });
}

function setDefaultImage(vin) {
  const imgElement = document.getElementById('vehicle-image-' + vin);
  imgElement.src = '/static/images/no_image_available.png'; // Path to your default image
  imgElement.alt = 'No Image Available';
}

// Example usage:
// Assuming you have a VIN and an img tag with an id 'vehicle-image-<VIN>'
displayVehicleImage('1GNALDEK9FZ108495');

function getMaintenance(vin, mileage) {
  // Fetch maintenance info from the API
  const url = `/maintenance_info?vin=${vin}&mileage=${mileage}`;

  fetch(url)
    .then(response => response.json())
    .then(data => {
      if (data.message.code === 0) {
        const maintenanceInfoDiv = document.getElementById("maintenanceInfo");
        maintenanceInfoDiv.innerHTML = '';

        // Display maintenance info for the vehicle
        data.data.forEach(item => {
          maintenanceInfoDiv.innerHTML += `<p><strong>${item.desc}</strong> - Due at ${item.due_mileage} miles - Estimated Cost: $${item.repair.total_cost.toFixed(2)}</p>`;
        });

        // Show the modal with the fetched data
        modal.style.display = "block";
      } else {
        throw new Error(data.message.message);
      }
    })
    .catch(error => {
      console.error('Error fetching maintenance info:', error);
      document.getElementById("maintenanceInfo").innerHTML = 'Failed to fetch maintenance information.';
      modal.style.display = "block";
    });
}
