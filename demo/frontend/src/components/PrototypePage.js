import React, { useState, useRef, useCallback } from 'react';
import {
  Box,
  Button,
  Step,
  StepLabel,
  Stepper,
  Typography,
  MenuItem,
  Select,
  InputLabel,
  FormControl,
  Modal, // Import Modal for the popup
  LinearProgress, // Import LinearProgress for the progress bar
} from '@mui/material';
import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts'; // Import recharts components
import Slider from 'react-slick'; // Import react-slick
import 'slick-carousel/slick/slick.css'; // Import slick-carousel CSS
import 'slick-carousel/slick/slick-theme.css'; // Import slick-carousel theme CSS
import './PrototypePage.css';

const steps = [
  'Create Script (Info)',
  'Create Script (Rules)',
  'Run Audit',
  'Generate Report',
];

const useDebounce = (callback, delay) => {
  const timerRef = useRef();

  const debouncedCallback = useCallback(
    (...args) => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
      timerRef.current = setTimeout(() => {
        callback(...args);
      }, delay);
    },
    [callback, delay]
  );

  return debouncedCallback;
};

const PrototypePage = () => {
  const [activeStep, setActiveStep] = useState(0);
  const sliderRef = React.useRef(null);


  const debouncedHandleNext = useDebounce(() => {
    if (sliderRef.current && activeStep < steps.length - 1) {
      setActiveStep((prevActiveStep) => prevActiveStep + 1);
      sliderRef.current.slickNext();
    }
  }, 50); // 300ms debounce delay

  const debouncedHandleBack = useDebounce(() => {
    if (sliderRef.current && activeStep > 0) {
      setActiveStep((prevActiveStep) => prevActiveStep - 1);
      sliderRef.current.slickPrev();
    }
  }, 50);

  const handleNext = () => {
    if (activeStep === 2) {
      // If the active step is "Run Audit", open the modal and start the audit
      setOpenModal(true);
      setProgress(0);
      startAuditProcess();
    } else {
      debouncedHandleNext();
    }
  };

  const handleBack = () => {
    debouncedHandleBack();
  };

  const handleRestart = () => {
    setActiveStep(0);
    if (sliderRef.current) {
      sliderRef.current.slickGoTo(0);
    }
  };

  const handleDotClick = (index) => {
    setActiveStep(index);
    if (sliderRef.current) {
      sliderRef.current.slickGoTo(index);
    }
  };

  const sliderSettings = {
    dots: true,
    infinite: false,
    arrows: false,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    initialSlide: activeStep, // Ensure slider starts at the active step
    adaptiveHeight: true,
    swipe: false, // Disable swipe to stabilize layout
    touchMove: false, // Prevent touch from affecting layout
    afterChange: (current) => setActiveStep(current), // Sync slider state after change
    appendDots: (dots) => (
      <div
        style={{
          position: 'fixed',
          bottom: '3rem', // Align with Next and Back buttons
          left: '50%',
          transform: 'translateX(-50%)',
          textAlign: 'center',
          zIndex: 10, // Ensure dots stay on top
          display: 'flex',
          justifyContent: 'center', // Center the dots
        }}
      >
        <ul style={{ margin: '0', padding: '0', display: 'flex' }}>{dots}</ul>
      </div>
    ),
    customPaging: (i) => (
      <div
        style={{
          width: '10px',
          height: '10px',
          borderRadius: '50%',
          backgroundColor: activeStep === i ? '#FFB300' : '#1976d2', // Yellow for active dot, blue for others
          display: 'inline-block',
          margin: '0 5px',
          transition: 'background-color 0.3s ease', // Smooth transition for color change
        }}
      ></div>
    ),
  };

  // Function to handle dropdown focus and blur to maintain layout
  const handleDropdownOpen = (event) => {
    // Stop propagation if needed to avoid affecting slider layout
    event.stopPropagation();
  };

  const handleDropdownClose = (event) => {
    // Stop propagation to ensure other interactions aren't affected
    event.stopPropagation();
  };

  const [rules, setRules] = useState([{ text: '', method: 'Manual' }]); // Initialize rules state with one rule
  const [isHovered, setIsHovered] = useState(false); // Define the hover state

  // Define hover states for the '+' button and the action buttons
  const [isAddButtonHovered, setIsAddButtonHovered] = useState(false);
  const [isActionButtonsVisible, setIsActionButtonsVisible] = useState(false);

  // Function to handle when the mouse enters the add button area
  const handleAddButtonMouseEnter = () => {
    setIsAddButtonHovered(true);
    setIsActionButtonsVisible(true);
  };

  // Update the event handlers for mouse enter and leave on the action buttons
  const handleActionButtonsMouseEnter = () => {
    setIsAddButtonHovered(true);
  };

  // Function to handle when the mouse leaves the action buttons area
  const handleActionButtonsMouseLeave = () => {
    setIsAddButtonHovered(false);
    setIsActionButtonsVisible(false);
  };

  // Function to add a manual rule
  const handleAddManualRule = () => {
    setRules((prevRules) => [...prevRules, { text: '', method: 'Manual' }]);
  };

  // Function to add a rule with magic
  const handleAddMagicRule = () => {
    setRules((prevRules) => [
      ...prevRules,
      { text: '', method: 'Using Natural Language' },
    ]);
  };

  // Function to handle changes in rule text
  const handleRuleChange = (index, value) => {
    setRules((prevRules) =>
      prevRules.map((rule, i) => (i === index ? { ...rule, text: value } : rule))
    );
  };

  // Function to remove a rule
  const handleRemoveRule = (index) => {
    if (rules.length > 1) {
      // Ensure there's always at least one rule
      setRules((prevRules) => prevRules.filter((_, i) => i !== index));
    }
  };

  // Styles for gradient animation and hover effects
  const gradientAnimation = {
    background:
      'linear-gradient(270deg, #ff9a9e, #fad0c4, #fad0c4, #fbc2eb, #a18cd1, #fbc2eb, #fad0c4, #ff9a9e)',
    backgroundSize: '200% 200%',
    animation: 'gradient-animation 6s ease infinite',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    color: 'transparent',
  };

  const gradientBackground = {
    background:
      'linear-gradient(270deg, #ff9a9e, #fad0c4, #fad0c4, #fbc2eb, #a18cd1, #fbc2eb, #fad0c4, #ff9a9e)',
    backgroundSize: '200% 200%',
    animation: 'gradient-animation 6s ease infinite',
    color: 'lightyellow',
  };

  const hoverStyles = {
    gradientButton: {
      ...gradientBackground,
      transition: 'all 0.3s ease',
      '&:hover': {
        filter: 'brightness(1.2)', // Slightly brighten on hover
      },
    },
    manualButton: {
      transition: 'all 0.3s ease',
      '&:hover': {
        backgroundColor: 'yellow',
        color: 'black',
      },
    },
  };

  // Ensure the ref is always an object
  const buttonHideTimeoutsRef = useRef({});

  // Function to handle mouse enter on the textarea
  const handleRuleMouseEnter = (index, textarea, button) => {
    // Initialize the current ref as an empty object if it's null
    if (!buttonHideTimeoutsRef.current) {
      buttonHideTimeoutsRef.current = {};
    }

    // Clear the timeout if it exists
    if (buttonHideTimeoutsRef.current[index]) {
      clearTimeout(buttonHideTimeoutsRef.current[index]);
      buttonHideTimeoutsRef.current[index] = null;
    }

    // Show the button
    textarea.classList.add('text-shifted'); // Add class to shift text
    button.style.left = '10px'; // Move button from the left
    button.style.opacity = '1'; // Make button visible
    button.style.pointerEvents = 'auto'; // Ensure button is always clickable
  };

  // Function to handle mouse leave on the textarea
  const handleRuleMouseLeave = (index, textarea, button) => {
    // Initialize the current ref as an empty object if it's null
    if (!buttonHideTimeoutsRef.current) {
      buttonHideTimeoutsRef.current = {};
    }

    // Set the timeout to hide the button
    buttonHideTimeoutsRef.current[index] = setTimeout(() => {
      textarea.classList.remove('text-shifted'); // Remove class to shift text back
      button.style.left = '-90px'; // Hide button to the left
      button.style.opacity = '0'; // Make button invisible
    }, 500); // Delay of 0.5 seconds
  };

  // Function to handle mouse enter on Gen Rule button
  const handleButtonMouseEnter = (index, button) => {
    // Initialize the current ref as an empty object if it's null
    if (!buttonHideTimeoutsRef.current) {
      buttonHideTimeoutsRef.current = {};
    }

    // Clear the timeout if it exists
    if (buttonHideTimeoutsRef.current[index]) {
      clearTimeout(buttonHideTimeoutsRef.current[index]);
      buttonHideTimeoutsRef.current[index] = null;
    }

    // Show the button
    button.style.opacity = '1'; // Ensure button remains visible
    button.style.pointerEvents = 'auto'; // Ensure button is clickable
  };

  // Function to handle mouse leave on Gen Rule button
  const handleButtonMouseLeave = (index, textarea, button) => {
    // Initialize the current ref as an empty object if it's null
    if (!buttonHideTimeoutsRef.current) {
      buttonHideTimeoutsRef.current = {};
    }

    // Set the timeout to hide the button
    buttonHideTimeoutsRef.current[index] = setTimeout(() => {
      textarea.classList.remove('text-shifted'); // Remove class to shift text back
      button.style.left = '-90px'; // Hide button to the left
      button.style.opacity = '0'; // Make button invisible
    }, 500); // Delay of 0.5 seconds
  };

  const [showPassword, setShowPassword] = useState(false);
  const [targetSystemType, setTargetSystemType] = useState(''); // For handling select change
  const [username, setUsername] = useState(''); // For handling username input change
  const [ipAddress, setIpAddress] = useState(''); // For handling IP address input change
  const [port, setPort] = useState(''); // For handling port input change
  const [password, setPassword] = useState(''); // For handling password input change

  const handleSystemTypeChange = (event) => {
    setTargetSystemType(event.target.value);
  };

  const menuProps = {
    PaperProps: {
      style: {
        maxHeight: 300, // Adjust max height to fit your needs
        overflowY: 'auto', // Ensure dropdown is scrollable if needed
      },
    },
    MenuListProps: {
      disablePadding: true, // Disable padding to better control layout
    },
    disableScrollLock: true, // Prevents scroll lock on the body when dropdown is open
  };
  
  const [openModal, setOpenModal] = useState(false); // State to handle modal open/close
  const [progress, setProgress] = useState(0); // State to handle progress bar

  const ProgressTracker = ({ progress }) => {
    const stages = ['Connecting', 'Executing', 'Analyzing', 'Done'];
    const activeStage = Math.floor(progress / (100 / stages.length));
  
    return (
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          mb: 2,
          position: 'relative',
        }}
      >
        {stages.map((stage, index) => (
          <React.Fragment key={index}>
            <Box
              sx={{
                position: 'relative',
                zIndex: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                transition: 'transform 0.3s ease-in-out', // Add transition for scaling
              }}
            >
              <Box
                sx={{
                  width: 20,
                  height: 20,
                  borderRadius: '50%',
                  backgroundColor: index <= activeStage ? '#FFD700' : '#1976d2',
                  mb: 1,
                  transition: 'background-color 0.3s ease-in-out, transform 0.3s ease-in-out', // Smooth transition for color and transform
                  transform: index <= activeStage ? 'scale(1.2)' : 'scale(1)', // Scale active dot
                  boxShadow: index <= activeStage ? '0 0 10px #FFD700' : 'none', // Add glow to active dot
                }}
              />
              <Typography
                sx={{
                  color: index <= activeStage ? '#FFD700' : 'lightyellow',
                  fontFamily: 'MonoLisa',
                  fontSize: '0.75rem',
                  textAlign: 'center',
                }}
              >
                {stage}
              </Typography>
            </Box>
            {index < stages.length - 1 && (
              <Box
                sx={{
                  flex: 1,
                  height: 2,
                  backgroundColor:
                    index < activeStage ? '#FFD700' : '#1976d2',
                  transition: `width 0.3s ease-in-out ${
                    index === activeStage - 1 ? '0.3s' : '0s'
                  }`, // Sequential transition delay
                  position: 'relative',
                  top: 10,
                  marginLeft: 1,
                  marginRight: 1,
                  width: index <= activeStage ? '100%' : '0%',
                  transformOrigin: 'left center', // Define transform origin for scaling
                }}
              />
            )}
          </React.Fragment>
        ))}
      </Box>
    );
  };
  
  const startAuditProcess = () => {
    // Simulate the audit process with timeouts for each stage
    const stages = [1, 2, 3, 4]; // Represents 4 stages: Connect, Execute, Analyze, Complete
  
    stages.forEach((stage, index) => {
      setTimeout(() => {
        if (index < stages.length - 1) {
          // Update progress by 33% for each of the first three stages
          setProgress((index + 1) * 33); // Directly progress to the correct percentage
        } else {
          // Directly set progress to 100% on the final stage
          setProgress(100);
        }
  
        if (index === stages.length - 1) {
          // When the last stage is complete, set active step to "Generate Report"
          setActiveStep(3);
        }
      }, index * 1000); // Adjust the delay so the first stage starts at 0 ms
    });
  };
  
  const handleModalClose = () => {
    setOpenModal(false);
    // Ensure the step is set to the "Generate Report" page after closing the modal
    setActiveStep(3);
    sliderRef.current.slickGoTo(3); // Ensure slider moves to the correct step
  };

  // Fake data for the pie chart
  const pieData = [
    { name: 'Passed', value: 6 },
    { name: 'Failed', value: 4 },
  ];

  // Colors for the pie chart
  const COLORS = ['#4caf50', '#f44336'];
  const conditionMet = rules.every((rule) => rule.status === 'Pass');

  // Fake evidence data for audit results, related to NIST 800-53 controls
  const auditEvidence = [
    {
      control: 'AC-6 (1)',
      rule: "Ensure 'Least Privilege' is enforced",
      description: "The information system enforces the most restrictive set of rights/privileges or accesses needed by users.",
      status: 'Pass',
      value: 'Configured',
    },
    {
      control: 'AC-6 (2)',
      rule: "Ensure 'Privileged Accounts' are monitored",
      description: "Privileged accounts are regularly audited to ensure compliance with security policies.",
      status: 'Fail',
      value: 'Not Monitored',
    },
    {
      control: 'AC-6 (3)',
      rule: "Ensure 'Access Control' policies are applied",
      description: "Access control policies must be applied consistently across the information system.",
      status: 'Pass',
      value: 'Applied',
    },
    {
      control: 'AC-6 (4)',
      rule: "Ensure 'Remote Access' is restricted",
      description: "Remote access is restricted to authorized users only.",
      status: 'Pass',
      value: 'Restricted',
    },
    {
      control: 'AC-6 (5)',
      rule: "Ensure 'User Access Reviews' are conducted",
      description: "Regular reviews of user access are conducted to ensure the principle of least privilege is maintained.",
      status: 'Fail',
      value: 'Not Reviewed',
    },
    {
      control: 'AC-6 (6)',
      rule: "Ensure 'Audit Logs' are enabled",
      description: "Audit logs are enabled to track access and modifications.",
      status: 'Pass',
      value: 'Enabled',
    },
    {
      control: 'AC-6 (7)',
      rule: "Ensure 'Role-Based Access Control' is implemented",
      description: "Role-based access control is implemented to ensure proper segregation of duties.",
      status: 'Pass',
      value: 'Implemented',
    },
    {
      control: 'AC-6 (8)',
      rule: "Ensure 'Temporary Accounts' are disabled",
      description: "Temporary accounts are disabled after use to prevent unauthorized access.",
      status: 'Fail',
      value: 'Active',
    },
    {
      control: 'AC-6 (9)',
      rule: "Ensure 'Password Policies' are enforced",
      description: "Password policies are enforced to enhance security.",
      status: 'Pass',
      value: 'Enforced',
    },
    {
      control: 'AC-6 (10)',
      rule: "Ensure 'Two-Factor Authentication' is enabled",
      description: "Two-factor authentication is enabled for all privileged accounts.",
      status: 'Fail',
      value: 'Disabled',
    },
  ];

  return (
    <Box
      sx={{
        width: '100%',
        p: 3,
        backgroundColor: 'gray.900',
        minHeight: '100vh',
        color: 'lightyellow',
        fontFamily: 'MonoLisa',
        position: 'relative',
        paddingBottom: '4rem',
      }}
    >
      <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
        {steps.map((label, index) => (
          <Step key={label}>
            <StepLabel
              StepIconProps={{
                sx: {
                  color:
                    index === activeStep
                      ? '#FFB300'
                      : '#1976d2',
                },
              }}
              sx={{
                '& .MuiStepLabel-label': {
                  color:
                    index < activeStep
                      ? 'lightblue'
                      : index === activeStep
                      ? '#FFD700 !important'
                      : 'lightblue',
                  fontFamily: 'MonoLisa',
                },
                '& .MuiStepLabel-iconContainer': {
                  color:
                    index === activeStep
                      ? '#FFB300'
                      : '#1976d2',
                },
                '& .Mui-active .MuiStepLabel-label': {
                  color: '#FFD700 !important',
                },
                '& .MuiStepLabel-iconContainer .MuiSvgIcon-root': {
                  color:
                    index === activeStep
                      ? '#FFB300'
                      : '#1976d2',
                },
              }}
            >
              {label}
            </StepLabel>
          </Step>
        ))}
      </Stepper>

      <Slider {...sliderSettings} ref={sliderRef}>
        <Box sx={{ p: 2, fontFamily: 'MonoLisa' }}>
          <Typography
            variant="h6"
            component="div"
            sx={{ mb: 2, fontFamily: 'MonoLisa' }}
          >
            Information
          </Typography>
          {/* Add script writing logic here */}
          <Typography variant="body1" sx={{ fontFamily: 'MonoLisa', mb: 2 }}>
            Enter the script information below.
          </Typography>

            {/* Script Name Input */}
            <div className="relative mb-4 flex w-full flex-wrap items-stretch">
              <input
                type="text"
                className="custom-input" // Apply custom class
                placeholder="Script Name"
                aria-label="Script Name"
                aria-describedby="basic-addon1"
                style={{ minWidth: '400px' }} // Set consistent width
              />
            </div>

            {/* Description Input */}
            <div className="relative mb-4 flex w-full flex-wrap items-stretch">
              <input
                type="text"
                className="custom-input" // Apply custom class
                placeholder="Description"
                aria-label="Description"
                aria-describedby="basic-addon2"
                style={{ minWidth: '400px' }} // Set consistent width
              />
            </div>

            {/* Rational Input */}
            <div className="relative mb-4 flex w-full flex-wrap items-stretch">
              <input
                type="text"
                className="custom-input" // Apply custom class
                placeholder="Rational"
                aria-label="Rational"
                style={{ minWidth: '400px' }} // Set consistent width
              />
            </div>

            {/* Mitigation Input */}
            <div className="relative mb-4 flex w-full flex-wrap items-stretch">
              <input
                type="text"
                className="custom-input" // Apply custom class
                placeholder="Mitigation"
                aria-label="Mitigation"
                style={{ minWidth: '400px' }} // Set consistent width
              />
            </div>

          {/* Detection Method Select */}
          <div className="relative mb-4 flex w-full flex-wrap items-stretch">
            <FormControl fullWidth variant="outlined" className="flex-auto">
              <InputLabel
                id="detection-method-label"
                sx={{
                  fontFamily: 'MonoLisa',
                  color: 'lightyellow',
                  '&.Mui-focused': { color: 'lightyellow' },
                }} // Apply custom font
              >
                Detection Method
              </InputLabel>

              <Select
                labelId="detection-method-label"
                id="detection-method"
                label="Detection Method"
                onFocus={handleDropdownOpen}
                onBlur={handleDropdownClose}
                MenuProps={menuProps} // Apply MenuProps here
                sx={{
                  fontFamily: 'MonoLisa',
                  color: 'lightyellow',
                  '& .MuiSelect-icon': { color: 'lightyellow' },
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: 'lightyellow' },
                  '&:hover .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'primary.main',
                  },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'primary.main',
                  },
                }}
              >
                <MenuItem value="auto" sx={{ fontFamily: 'MonoLisa' }}>
                  Auto
                </MenuItem>
                <MenuItem value="semi-auto" sx={{ fontFamily: 'MonoLisa' }}>
                  Semi-Auto
                </MenuItem>
                <MenuItem value="manual" sx={{ fontFamily: 'MonoLisa' }}>
                  Manual
                </MenuItem>
              </Select>
            </FormControl>
          </div>

          {/* OS & Version Select */}
          <div className="relative mb-4 flex w-full flex-wrap items-stretch">
            <FormControl fullWidth variant="outlined" className="flex-auto">
              <InputLabel
                id="os-version-label"
                sx={{
                  fontFamily: 'MonoLisa',
                  color: 'lightyellow',
                  '&.Mui-focused': { color: 'lightyellow' },
                }} // Apply custom font
              >
                OS & Version
              </InputLabel>
              <Select
                labelId="os-version-label"
                id="os-version"
                label="OS & Version"
                MenuProps={menuProps} // Apply MenuProps here
                sx={{
                  fontFamily: 'MonoLisa', // Apply custom font
                  color: 'lightyellow',
                  '& .MuiSelect-icon': { color: 'lightyellow' },
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: 'lightyellow' },
                  '&:hover .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'primary.main',
                  },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'primary.main',
                  },
                }}
              >
                <MenuItem value="ubuntu22.04" sx={{ fontFamily: 'MonoLisa' }}>
                  Ubuntu 22.04
                </MenuItem>
                <MenuItem value="windows10" sx={{ fontFamily: 'MonoLisa' }}>
                  Windows 10
                </MenuItem>
                {/* Add more OS versions as needed */}
              </Select>
            </FormControl>
          </div>

          {/* Compliance Select */}
          <div className="relative mb-4 flex w-full flex-wrap items-stretch">
            <FormControl fullWidth variant="outlined" className="flex-auto">
              <InputLabel
                id="compliance-label"
                sx={{
                  fontFamily: 'MonoLisa',
                  color: 'lightyellow',
                  '&.Mui-focused': { color: 'lightyellow' },
                }} // Apply custom font
              >
                Compliance
              </InputLabel>
              <Select
                labelId="compliance-label"
                id="compliance"
                label="Compliance"
                MenuProps={menuProps} // Apply MenuProps here
                sx={{
                  fontFamily: 'MonoLisa', // Apply custom font
                  color: 'lightyellow',
                  '& .MuiSelect-icon': { color: 'lightyellow' },
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: 'lightyellow' },
                  '&:hover .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'primary.main',
                  },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'primary.main',
                  },
                }}
              >
                <MenuItem value="nist800-53r5" sx={{ fontFamily: 'MonoLisa' }}>
                  NIST 800-53r5
                </MenuItem>
                {/* Add more compliance frameworks as needed */}
              </Select>
            </FormControl>
          </div>

          {/* Control Select */}
          <div className="relative mb-4 flex w-full flex-wrap items-stretch">
            <FormControl fullWidth variant="outlined" className="flex-auto">
              <InputLabel
                id="control-label"
                sx={{
                  fontFamily: 'MonoLisa',
                  color: 'lightyellow',
                  '&.Mui-focused': { color: 'lightyellow' },
                }} // Apply custom font
              >
                Control
              </InputLabel>
              <Select
                labelId="control-label"
                id="control"
                label="Control"
                MenuProps={menuProps} // Apply MenuProps here
                sx={{
                  fontFamily: 'MonoLisa', // Apply custom font
                  color: 'lightyellow',
                  '& .MuiSelect-icon': { color: 'lightyellow' },
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: 'lightyellow' },
                  '&:hover .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'primary.main',
                  },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'primary.main',
                  },
                }}
              >
                {/* Add controls based on selected compliance */}
              </Select>
            </FormControl>
          </div>
        </Box>

        <Box sx={{ p: 2, fontFamily: 'MonoLisa' }}>
          <Typography
            variant="h6"
            component="div"
            sx={{ mb: 2, fontFamily: 'MonoLisa' }}
          >
            Rules
          </Typography>
          <Typography variant="body1" sx={{ fontFamily: 'MonoLisa', mb: 2 }}>
            Specify the rules for your script below.
          </Typography>

          {/* Condition Select */}
          <div className="relative mb-4 flex w-full flex-wrap items-stretch">
            <FormControl
              fullWidth
              variant="outlined"
              className="flex-auto"
              sx={{
                mb: 2,
                '& .MuiInputBase-root': {
                  pr: '2rem', // Add padding to prevent content shift
                  minWidth: '200px', // Set a fixed minimum width for dropdown to stabilize layout
                },
                '& .MuiSelect-select': {
                  minWidth: '200px', // Consistent width for the select options
                },
              }}
            >
              <InputLabel
                id="condition-label"
                sx={{
                  fontFamily: 'MonoLisa',
                  color: 'lightyellow',
                  '&.Mui-focused': { color: 'lightyellow' },
                }}
              >
                Condition
              </InputLabel>
              <Select
                labelId="condition-label"
                id="condition"
                label="Condition"
                MenuProps={menuProps} // Apply MenuProps here
                sx={{
                  fontFamily: 'MonoLisa',
                  color: 'lightyellow',
                  '& .MuiSelect-icon': { color: 'lightyellow' },
                  '& .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'lightyellow',
                  },
                  '&:hover .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'primary.main',
                  },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'primary.main',
                  },
                  minWidth: '200px', // Maintain consistent width
                }}
              >
                <MenuItem value="any" sx={{ fontFamily: 'MonoLisa' }}>
                  Any
                </MenuItem>
                <MenuItem value="none" sx={{ fontFamily: 'MonoLisa' }}>
                  None
                </MenuItem>
                <MenuItem value="all" sx={{ fontFamily: 'MonoLisa' }}>
                  All
                </MenuItem>
              </Select>
            </FormControl>
          </div>

          {/* Rules Input */}
          <div className="relative mb-4 flex flex-col w-full flex-wrap items-stretch">
            {rules.map((rule, index) => (
              <div key={index} className="relative mb-2 flex items-center group">
                <div className="relative flex items-center flex-auto">
                  <textarea
                    className={`relative z-10 m-0 block flex-auto rounded ${
                      rule.method === 'Using Natural Language'
                        ? 'magicRule'
                        : 'manualRule'
                    } bg-clip-padding text-base font-normal leading-[1.6] outline-none transition duration-200 ease-in-out placeholder:text-neutral-500 focus:z-[3] focus:border-primary focus:shadow-inset focus:outline-none motion-reduce:transition-none dark:placeholder:text-neutral-200 dark:autofill:shadow-autofill dark:focus:border-primary`}
                    placeholder={`Rule ${index + 1} (${rule.method})`}
                    aria-label={`Rule ${index + 1}`}
                    value={rule.text}
                    onChange={(e) => handleRuleChange(index, e.target.value)}
                    onMouseEnter={(e) => {
                      const textarea = e.currentTarget;
                      const button =
                        textarea.parentNode.querySelector('.gen-rule-button');
                      if (textarea && button) {
                        handleRuleMouseEnter(index, textarea, button);
                      }
                    }}
                    onMouseLeave={(e) => {
                      const textarea = e.currentTarget;
                      const button =
                        textarea.parentNode.querySelector('.gen-rule-button');
                      if (textarea && button) {
                        handleRuleMouseLeave(index, textarea, button);
                      }
                    }}
                    style={{
                      height: '4rem',
                      resize: 'none',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'flex-start', // Align text to left
                      overflow: 'hidden',
                      paddingTop: '1rem', // Vertically center text by adjusting padding
                      paddingBottom: '1rem', // Vertically center text by adjusting padding
                      position: 'relative', // Ensure text area is positioned correctly
                    }}
                  ></textarea>
                  {rule.method === 'Using Natural Language' && (
                    <button
                      type="button"
                      className="gradientButtonHovered gen-rule-button"
                      onClick={() => console.log('Gen Rule clicked')}
                      onMouseEnter={(e) => {
                        const button = e.currentTarget;
                        handleButtonMouseEnter(index, button);
                      }}
                      onMouseLeave={(e) => {
                        const textarea =
                          e.currentTarget.parentNode.querySelector('textarea');
                        const button = e.currentTarget;
                        handleButtonMouseLeave(index, textarea, button);
                      }}
                      style={{
                        position: 'absolute',
                        left: '10px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        zIndex: 11, // Ensure the button is above the text area
                        pointerEvents: 'auto', // Ensure button is always clickable
                      }}
                    >
                      Gen Rule
                    </button>
                  )}
                </div>
                {rules.length > 1 && (
                  <button
                    type="button"
                    className="absolute z-10 right-2 top-1/2 transform -translate-y-1/2 w-8 h-8 bg-red-600 text-lightyellow rounded-full opacity-0 group-hover:opacity-100 hover:bg-red-700 transition duration-300 flex items-center justify-center"
                    onClick={() => handleRemoveRule(index)}
                    title="Delete rule"
                  >
                    &times;
                  </button>
                )}
              </div>
            ))}

            <div
              className="relative mt-2 w-full flex justify-center add-rule-container"
              onMouseEnter={handleActionButtonsMouseEnter}
              onMouseLeave={handleActionButtonsMouseLeave}
            >
              {isActionButtonsVisible ? (
                <div className="absolute w-full flex justify-between">
                  <button
                    type="button"
                    className="manualButton flex-1 mx-2" // Standard button class for manual rule
                    onClick={handleAddManualRule}
                    style={{
                      cursor: 'pointer',
                      marginRight: '0.1rem', // Add space between buttons
                      transform: 'scale(0.99)', // Slightly reduce size to prevent cutoff
                    }}
                  >
                    Add Rule Manually
                  </button>
                  <button
                    type="button"
                    className={`gradientButton flex-1 mx-2 ${isAddButtonHovered ? 'gradientButtonHovered' : ''}`} // Add gradient only on hover
                    onClick={handleAddMagicRule}
                    style={{
                      cursor: 'pointer',
                      marginLeft: '0.1rem', // Add space between buttons
                      transform: 'scale(0.99)', // Slightly reduce size to prevent cutoff
                    }}
                    onMouseEnter={() => setIsAddButtonHovered(true)} // Start gradient effect on hover
                    onMouseLeave={() => setIsAddButtonHovered(false)} // Remove gradient effect on leave
                  >
                    Add Rule With GenAI
                  </button>
                </div>
              ) : (
                <button
                  type="button"
                  className="relative w-full text-center bg-transparent border border-solid border-neutral-200 rounded py-[0.25rem] text-base font-normal leading-[1.6] text-lightyellow transition duration-300"
                  onMouseEnter={handleAddButtonMouseEnter}
                  style={{ marginBottom: '0.5rem' }}
                >
                  +
                </button>
              )}
            </div>
          </div>
        </Box>

        <Box sx={{ p: 2, fontFamily: 'MonoLisa' }}>
          <Typography
            variant="h6"
            component="div"
            sx={{ mb: 2, fontFamily: 'MonoLisa' }}
          >
            Select Target System
          </Typography>

          <Typography variant="body1" sx={{ fontFamily: 'MonoLisa', mb: 2 }}>
          In this step, enter the connection details for the target system you want to audit.<br />
          The system will connect to the target endpoint via SSH to perform the audit.
          </Typography>

          {/* Target System Name Input */}
          <div className="relative mb-4 flex w-full flex-wrap items-stretch">
            <input
              type="text"
              className="custom-input" // Apply custom class
              placeholder="Target System Name"
              aria-label="Target System Name"
            />
          </div>

          {/* Target System Type Select */}
          <div className="relative mb-4 flex w-full flex-wrap items-stretch">
            <FormControl fullWidth variant="outlined" className="flex-auto">
              <InputLabel
                id="target-system-type-label"
                sx={{
                  fontFamily: 'MonoLisa',
                  color: 'lightyellow',
                  '&.Mui-focused': { color: 'lightyellow' },
                }} // Apply custom font
              >
                Target System Type
              </InputLabel>
              <Select
                labelId="target-system-type-label"
                id="target-system-type"
                value={targetSystemType} // Add value for controlled component
                onChange={handleSystemTypeChange} // Add onChange event
                label="Target System Type"
                MenuProps={menuProps} // Apply MenuProps here
                sx={{
                  fontFamily: 'MonoLisa', // Apply custom font
                  color: 'lightyellow',
                  '& .MuiSelect-icon': { color: 'lightyellow' },
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: 'lightyellow' },
                  '&:hover .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'primary.main',
                  },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'primary.main',
                  },
                }}
              >
                <MenuItem value="ubuntu18.04" sx={{ fontFamily: 'MonoLisa' }}>
                  Ubuntu 18.04
                </MenuItem>
                <MenuItem value="ubuntu20.04" sx={{ fontFamily: 'MonoLisa' }}>
                  Ubuntu 20.04
                </MenuItem>
                <MenuItem value="ubuntu22.04" sx={{ fontFamily: 'MonoLisa' }}>
                  Ubuntu 22.04
                </MenuItem>
                <MenuItem value="windows10" sx={{ fontFamily: 'MonoLisa' }}>
                  Windows 10
                </MenuItem>
                <MenuItem value="windows11" sx={{ fontFamily: 'MonoLisa' }}>
                  Windows 11
                </MenuItem>
              </Select>
            </FormControl>
          </div>

          {/* Port Input */}
          <div className="relative mb-4 flex w-full flex-wrap items-stretch">
            <input
              type="text"
              className="custom-input" // Apply custom class
              placeholder="Port"
              aria-label="Port"
              value={port} // Add value for controlled component
              onChange={(e) => setPort(e.target.value)} // Add onChange event
              style={{ minWidth: '400px' }} // Set fixed width
            />
          </div>

          {/* Username + IP Address Input */}
          <div className="relative mb-4 flex w-full flex-wrap items-stretch input-group">
            <input
              type="text"
              className="custom-input" // Apply custom class
              placeholder="Username"
              aria-label="Username"
              value={username} // Add value for controlled component
              onChange={(e) => setUsername(e.target.value)} // Add onChange event
              style={{ borderRadius: '4px 0 0 4px', flex: 1 }} // Use flex property to share space equally
            />
            <span className="at-symbol">@</span>
            <input
              type="text"
              className="custom-input" // Apply custom class
              placeholder="IP Address"
              aria-label="IP Address"
              value={ipAddress} // Add value for controlled component
              onChange={(e) => setIpAddress(e.target.value)} // Add onChange event
              style={{ borderRadius: '0 4px 4px 0', flex: 1 }} // Use flex property to share space equally
            />
          </div>

          {/* Password Input with Toggle Visibility */}
          <div className="relative mb-4 flex w-full flex-wrap items-stretch password-input">
            <input
              type={showPassword ? 'text' : 'password'} // Conditional input type
              className="custom-input" // Apply custom class
              placeholder="Password"
              aria-label="Password"
              value={password} // Add value for controlled component
              onChange={(e) => setPassword(e.target.value)} // Add onChange event
              style={{ paddingRight: '2.5rem', minWidth: '400px' }} // Add padding for eye icon and set width
            />
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              className="w-5 h-5 eye-icon"
              onClick={() => setShowPassword(!showPassword)} // Toggle password visibility
            >
              {showPassword ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                />
              )}
            </svg>
          </div>
        </Box>

        <Box sx={{ p: 2, fontFamily: 'MonoLisa', width: '50%', margin: '0 auto' }}>
          <Typography
            variant="h6"
            component="div"
            sx={{ mb: 2, fontFamily: 'MonoLisa', textAlign: 'left' }}
          >
            {steps[3]}
          </Typography>
          <Typography
            variant="body1"
            sx={{ fontFamily: 'MonoLisa', mb: 4, textAlign: 'left' }} // Increased bottom margin for spacing
          >
            Below is the summary of the audit checks performed.
          </Typography>

          {/* Summary Table */}
          <Box sx={{ mb: 3, overflowX: 'auto', display: 'flex', justifyContent: 'center' }}>
            <table
              style={{
                width: '50%',
                color: 'lightyellow',
                fontFamily: 'MonoLisa',
                borderCollapse: 'collapse',
                border: '1px solid lightyellow',
                marginBottom: '20px', // Add space between tables
              }}
            >
              <tbody>
                <tr>
                  <td
                    style={{
                      padding: '16px', // Increased padding for better spacing
                      borderBottom: '1px solid lightyellow',
                      width: '50%',
                      verticalAlign: 'middle', // Vertically center the text
                    }}
                  >
                    AC-6 Least Privilege Script
                  </td>
                  <td
                    style={{
                      padding: '16px', // Increased padding for better spacing
                      borderBottom: '1px solid lightyellow',
                      width: '50%',
                      textAlign: 'center',
                      verticalAlign: 'middle', // Vertically center the chart
                    }}
                  >
                    <PieChart width={200} height={200}>
                      <Pie
                        data={pieData}
                        cx="50%" // Center the pie chart horizontally
                        cy="50%" // Center the pie chart vertically
                        labelLine={false}
                        outerRadius={60} // Slightly larger radius for better visibility
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {pieData.map((entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={COLORS[index % COLORS.length]}
                          />
                        ))}
                      </Pie>
                      <Legend
                        layout="horizontal"
                        align="center"
                        verticalAlign="bottom"
                        iconType="circle" // Use circular icons for better aesthetics
                        wrapperStyle={{
                          marginTop: 10, // Add margin to separate legend from the chart
                          fontSize: '12px', // Smaller font size for legend items
                        }}
                      />
                    </PieChart>
                  </td>
                </tr>


                <tr>
                  <td
                    style={{
                      padding: '8px',
                      borderBottom: '1px solid lightyellow',
                    }}
                  >
                    Result
                  </td>
                  <td
                    style={{
                      padding: '8px',
                      borderBottom: '1px solid lightyellow',
                      color: conditionMet ? 'lightgreen' : 'lightcoral',
                    }}
                  >
                    {conditionMet ? 'PASS' : 'FAIL'}
                  </td>
                </tr>
                <tr>
                  <td
                    style={{
                      padding: '8px',
                      borderBottom: '1px solid lightyellow',
                    }}
                  >
                    Description
                  </td>
                  <td
                    style={{
                      padding: '8px',
                      borderBottom: '1px solid lightyellow',
                    }}
                  >
                    Your Script Description
                  </td>
                </tr>
                <tr>
                  <td
                    style={{
                      padding: '8px',
                      borderBottom: '1px solid lightyellow',
                    }}
                  >
                    Rationale
                  </td>
                  <td
                    style={{
                      padding: '8px',
                      borderBottom: '1px solid lightyellow',
                    }}
                  >
                    Your Rationale
                  </td>
                </tr>
                <tr>
                  <td
                    style={{
                      padding: '8px',
                      borderBottom: '1px solid lightyellow',
                    }}
                  >
                    Mitigation
                  </td>
                  <td
                    style={{
                      padding: '8px',
                      borderBottom: '1px solid lightyellow',
                    }}
                  >
                    Your Mitigation Strategy
                  </td>
                </tr>
                <tr>
                  <td
                    style={{
                      padding: '8px',
                      borderBottom: '1px solid lightyellow',
                    }}
                  >
                    Detection Method
                  </td>
                  <td
                    style={{
                      padding: '8px',
                      borderBottom: '1px solid lightyellow',
                    }}
                  >
                    Your Detection Method
                  </td>
                </tr>
                <tr>
                  <td
                    style={{
                      padding: '8px',
                      borderBottom: '1px solid lightyellow',
                    }}
                  >
                    OS & Version
                  </td>
                  <td
                    style={{
                      padding: '8px',
                      borderBottom: '1px solid lightyellow',
                    }}
                  >
                    Your OS & Version
                  </td>
                </tr>
                <tr>
                  <td
                    style={{
                      padding: '8px',
                      borderBottom: '1px solid lightyellow',
                    }}
                  >
                    Compliance & Control
                  </td>
                  <td
                    style={{
                      padding: '8px',
                      borderBottom: '1px solid lightyellow',
                    }}
                  >
                    Your Compliance & Control Details
                  </td>
                </tr>
              </tbody>
            </table>
          </Box>

          {/* Evidence Table */}
          <Box sx={{ mb: 3, overflowX: 'auto', display: 'flex', justifyContent: 'center' }}>
            <table
              style={{
                width: '50%',
                color: 'lightyellow',
                fontFamily: 'MonoLisa',
                borderCollapse: 'collapse',
                border: '1px solid lightyellow',
              }}
            >
              <thead>
                <tr>
                  <th
                    style={{
                      textAlign: 'left',
                      padding: '8px',
                      borderBottom: '1px solid lightyellow',
                    }}
                  >
                    Condition
                  </th>
                  <th
                    style={{
                      textAlign: 'left',
                      padding: '8px',
                      borderBottom: '1px solid lightyellow',
                    }}
                  >
                    Rule
                  </th>
                  <th
                    style={{
                      textAlign: 'left',
                      padding: '8px',
                      borderBottom: '1px solid lightyellow',
                    }}
                  >
                    Description
                  </th>
                  <th
                    style={{
                      textAlign: 'left',
                      padding: '8px',
                      borderBottom: '1px solid lightyellow',
                    }}
                  >
                    Status
                  </th>
                  <th
                    style={{
                      textAlign: 'left',
                      padding: '8px',
                      borderBottom: '1px solid lightyellow',
                    }}
                  >
                    Value
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td
                    style={{
                      padding: '8px',
                      borderBottom: '1px solid lightyellow',
                    }}
                  >
                    All
                  </td>
                  <td colSpan={4}></td> {/* Empty cells spanning remaining columns */}
                </tr>
                {auditEvidence.map((evidence, index) => (
                  <tr key={index}>
                    <td></td> {/* Empty cell for Condition column */}
                    <td
                      style={{
                        padding: '8px',
                        borderBottom: '1px solid lightyellow',
                      }}
                    >
                      {evidence.rule}
                    </td>
                    <td
                      style={{
                        padding: '8px',
                        borderBottom: '1px solid lightyellow',
                      }}
                    >
                      {evidence.description}
                    </td>
                    <td
                      style={{
                        padding: '8px',
                        borderBottom: '1px solid lightyellow',
                        color: evidence.status === 'Pass' ? 'lightgreen' : 'lightcoral',
                      }}
                    >
                      {evidence.status}
                    </td>
                    <td
                      style={{
                        padding: '8px',
                        borderBottom: '1px solid lightyellow',
                      }}
                    >
                      {evidence.value}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Box>
        </Box>
      </Slider>

      <Modal
        open={openModal}
        onClose={handleModalClose}
        aria-labelledby="modal-modal-title"
        aria-describedby="modal-modal-description"
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backdropFilter: 'blur(5px)', // Add blur effect for background
          transition: 'opacity 0.3s ease-in-out', // Add transition for opacity
        }}
      >
        <Box
          sx={{
            position: 'relative',
            width: '600px', // Increase width for larger display
            bgcolor: 'gray.900',
            color: 'lightyellow',
            borderRadius: 2,
            boxShadow: 24,
            p: 4,
            fontFamily: 'MonoLisa', // Apply MonoLisa font
            transform: 'scale(1)', // Add scale for pop-up effect
            transition: 'transform 0.3s ease-in-out, opacity 0.3s ease-in-out', // Transition for scale and opacity
            '&:focus': { outline: 'none' }, // Remove focus outline
          }}
        >
          <Typography
            id="modal-modal-title"
            variant="h6"
            component="h2"
            sx={{ mb: 2, fontFamily: 'MonoLisa' }} // Ensure font is applied to title
          >
            Audit Progress
          </Typography>

          {/* Progress Tracker component for visual representation */}
          <ProgressTracker progress={progress} />

          {/* Progress Bar with percentage text */}
          <Box
            sx={{
              width: '100%',
              backgroundColor: '#4a4a4a',
              borderRadius: 5, // Rounded corners for progress bar
              overflow: 'hidden',
              mb: 2,
              position: 'relative',
            }}
          >
            <Box
              sx={{
                width: `${progress}%`,
                backgroundColor: '#FFD700',
                p: 0.5,
                textAlign: 'center',
                fontSize: '0.75rem',
                fontWeight: 'medium',
                color: 'black',
                fontFamily: 'MonoLisa',
                transition: 'width 0.3s ease-in-out', // Smooth width transition
              }}
            >
              {`${progress}%`}
            </Box>
          </Box>

          <Typography
            id="modal-modal-description"
            sx={{ mt: 2, fontFamily: 'MonoLisa' }} // Ensure font is applied to description
          >
            {progress === 100 ? 'Audit Complete!' : 'Audit in Progress...'}
          </Typography>
          {progress === 100 && (
            <Button
              onClick={handleModalClose}
              variant="contained"
              sx={{
                mt: 2,
                backgroundColor: '#1976d2',
                color: 'lightyellow',
                fontFamily: 'MonoLisa', // Apply MonoLisa font to button
                transition: 'transform 0.3s ease-in-out', // Add transition to button
                '&:hover': {
                  transform: 'scale(1.05)', // Slightly enlarge on hover
                  backgroundColor: '#ffd700',
                  color: 'lightyellow',
                },
              }}
            >
              Close
            </Button>
          )}
        </Box>
      </Modal>

      <Box
        sx={{
          position: 'fixed',
          bottom: '2.5rem',
          left: '2%',
          right: '10%',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          width: '95%',
          px: 3,
          backgroundColor: 'gray.900',
          zIndex: 10,
        }}
      >
        <Button
          disabled={activeStep === 0}
          onClick={handleBack}
          variant="contained"
          color="primary"
          sx={{
            transition: 'transform 0.3s',
            fontFamily: 'MonoLisa',
            backgroundColor: '#1976d2',
            color: 'lightyellow',
            '&:hover': {
              transform: 'scale(1.05)',
              backgroundColor: '#ffd700',
              color: 'lightyellow',
            },
          }}
        >
          Back
        </Button>
        {activeStep < steps.length - 1 ? (
          <Button
            variant="contained"
            color="primary"
            onClick={handleNext}
            sx={{
              transition: 'transform 0.3s',
              fontFamily: 'MonoLisa',
              backgroundColor: '#1976d2',
              color: 'lightyellow',
              '&:hover': {
                transform: 'scale(1.05)',
                backgroundColor: '#ffd700',
                color: 'lightyellow',
              },
            }}
          >
            {activeStep === 2 ? 'Start Audit' : 'Next'}
          </Button>
        ) : (
          <Button
            variant="contained"
            color="secondary"
            onClick={handleRestart}
            sx={{
              transition: 'transform 0.3s',
              fontFamily: 'MonoLisa',
              backgroundColor: '#1976d2',
              color: 'lightyellow',
              '&:hover': {
                transform: 'scale(1.05)',
                backgroundColor: '#ffd700',
                color: 'lightyellow',
              },
            }}
          >
            Restart
          </Button>
        )}
      </Box>
    </Box>
  );
};

export default PrototypePage;
