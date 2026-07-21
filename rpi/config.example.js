// ============================================================================
// CONFIGURATION
// Create a copy of this file named "config.js" and modify the values below 
// to configure your wallboard display.
// ============================================================================
const CONFIG = {
    // General display settings
    title: "MakeIt Labs Display",

    // Set backgroundVideo to a URL (e.g. "LaserRoom.mp4") to use a video background.
    // If null, it falls back to backgroundColors (for the standard template).
    backgroundVideo: null,
    backgroundColors: ["#111111", "#333333", "#555555", "#777777"],

    // Calendar query parameter (e.g. "auto", "metalshop", "laser", "textiles")
    calendarName: "auto",

    // URL for fetching notices (set to null if no notices exist for this display)
    // noticesUrl: "https://auth.makeitlabs.com/authit/api/v1/resources/auto-lift-users/notices",
    noticesUrl: null, 

    // MQTT Configuration
    mqtt: {
        // CRITICAL: Ensure clientId is unique per physical display board!
        clientId: 'wallboard-unique-id', 
        
        // Subscribes to displayboard/read/{topicBase}/#
        topicBase: 'auto', 

        // Map status topics to UI popup configuration. 
        // Provide a label, and optionally a bgColor for the popup.
        resources: {
            // "displayboard/read/status/autolift-primary": { label: "Auto Lift:", bgColor: "#8f8fffd0" },
            // "displayboard/read/status/laser-epilog": { label: "Epilog:", bgColor: "#8f8fffD0" }
        }
    }
};
