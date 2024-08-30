// React and Hooks
import React, { useState, useRef, useCallback, useEffect } from 'react';

// MUI Components
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
  Modal,
  Grid
} from '@mui/material';

// Charts
import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';

// Other Libraries
import axios from 'axios';
import Slider from 'react-slick';
import styled from 'styled-components';
import ReactMarkdown from 'react-markdown';

// Styles and Custom Components
import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';
import './PrototypePage.css';
import FloatingChat from '../FloatingChat/FloatingChat';

const StyledMarkdown = styled.div`
  h1 {
    color: #ffd700;
    font-size: 1.5rem;
    margin-bottom: 1rem;
  }
  
  h2 {
    color: #ffa500;
    font-size: 1.25rem;
    margin-bottom: 0.75rem;
  }

  h3 {
    color: #ff8c00;
    font-size: 1.125rem;
    margin-bottom: 0.5rem;
  }

  p {
    color: #f0e68c;
    margin-bottom: 0.5rem;
    line-height: 1.6;
  }

  ul {
    color: #f5deb3;
    padding-left: 1.5rem;
    margin-bottom: 0.5rem;
  }

  li {
    margin-bottom: 0.25rem;
  }

  strong {
    color: #ff6347;
  }

  em {
    color: #dda0dd;
  }

  code {
    color: #00ffff;
    background-color: #333;
    padding: 0.2rem;
    border-radius: 0.3rem;
  }

  blockquote {
    color: #7fffd4;
    border-left: 4px solid #7fffd4;
    padding-left: 1rem;
    margin: 1rem 0;
  }

  a {
    color: #add8e6;
    text-decoration: underline;
  }
`;

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
  const [showPassword, setShowPassword] = useState(false);
  const [isAddButtonHovered, setIsAddButtonHovered] = useState(false);
  const [isActionButtonsVisible, setIsActionButtonsVisible] = useState(false);
  const [targetSystemType, setTargetSystemType] = useState('');
  const [username, setUsername] = useState('');
  const [ipAddress, setIpAddress] = useState('');
  const [port, setPort] = useState('');
  const [password, setPassword] = useState('');
  const [rules, setRules] = useState([{ text: '', method: 'Manual' }]);
  const [scriptName, setScriptName] = useState('');
  const [description, setDescription] = useState('');
  const [rationale, setRationale] = useState('');
  const [mitigation, setMitigation] = useState('');
  const [detectionMethod, setDetectionMethod] = useState('');
  const [osVersion, setOsVersion] = useState('');
  const [complianceName, setComplianceName] = useState('');
  const [controlList, setControlList] = useState([]);
  const [condition, setCondition] = useState('all');
  const [targetSystemName, setTargetSystemName] = useState('');
  const [auditResults, setAuditResults] = useState(null);
  const [aiGeneratedSummary, setAiGeneratedSummary] = useState('');
  const [openModal, setOpenModal] = useState(false);
  const [progress, setProgress] = useState(0);
  const sliderRef = useRef(null);
  const buttonHideTimeoutsRef = useRef({});

  useEffect(() => {
    if (auditResults) {
      fetchAiSummary();
    }
  }, [auditResults]);

  // Slider Settings
  const sliderSettings = {
    dots: true,
    infinite: false,
    arrows: false,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    initialSlide: activeStep,
    adaptiveHeight: true,
    swipe: false,
    touchMove: false,
    afterChange: (current) => setActiveStep(current),
    appendDots: (dots) => (
      <div
        style={{
          position: 'fixed',
          bottom: '3rem',
          left: '50%',
          transform: 'translateX(-53.2%)',
          textAlign: 'center',
          zIndex: 10,
          display: 'flex',
          justifyContent: 'center',
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
          backgroundColor: activeStep === i ? '#FFB300' : '#1976d2',
          display: 'inline-block',
          margin: '0 5px',
          transition: 'background-color 0.3s ease',
        }}
      ></div>
    ),
  };

  // Handle Functions
  const handleNext = () => {
    if (activeStep === 2) {
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

  const handleSystemTypeChange = (event) => {
    setTargetSystemType(event.target.value);
  };

  const handleAddButtonMouseEnter = () => {
    setIsAddButtonHovered(true);
    setIsActionButtonsVisible(true);
  };

  const handleActionButtonsMouseEnter = () => {
    setIsAddButtonHovered(true);
  };

  const handleActionButtonsMouseLeave = () => {
    setIsAddButtonHovered(false);
    setIsActionButtonsVisible(false);
  };

  const handleAddManualRule = () => {
    setRules((prevRules) => [...prevRules, { text: '', method: 'Manual' }]);
  };

  const handleAddMagicRule = () => {
    setRules((prevRules) => [
      ...prevRules,
      { text: '', method: 'Using Natural Language' },
    ]);
  };

  const handleRuleChange = (index, value) => {
    setRules((prevRules) =>
      prevRules.map((rule, i) => (i === index ? { ...rule, text: value } : rule))
    );
  };

  const handleRemoveRule = (index) => {
    if (rules.length > 1) {
      setRules((prevRules) => prevRules.filter((_, i) => i !== index));
    }
  };

  const handleDropdownOpen = (event) => {
    event.stopPropagation();
  };
  
  const handleDropdownClose = (event) => {
    event.stopPropagation();
  };

  const handleAudit = async () => {
    const auditData = {
      scripts: [
        {
          script_name: scriptName,
          description: description,
          rationale: rationale,
          mitigation: mitigation,
          detection_method: detectionMethod,
          os_version: osVersion,
          compliances: [
            {
              name: complianceName,
              control_list: controlList
            }
          ],
          condition: condition,
          rules: rules.map((rule) => rule.text), // Send rules directly
        }
      ],
      ssh_info: {
        target_system_name: targetSystemName,
        target_system_type: targetSystemType,
        port: parseInt(port, 10), // Ensure port is an integer
        username: username,
        ip: ipAddress,
        password: password
      }
    };
  
    try {
      // Perform the audit API call
      const response = await fetch('http://127.0.0.1:8080/api/v1/audit/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(auditData), // Ensure auditData is the correct data to send
      });
  
      if (!response.ok) {
        throw new Error(`Audit failed: ${response.statusText}`);
      }
  
      // Process the response if needed
      const result = await response.json();
      console.log('Audit result:', result);
  
      // After successful audit, move to the next step
      handleNext();
  
    } catch (error) {
      console.error('Error executing audit:', error);
      // Handle the error (e.g., show an error message)
    }
  };  

  // Mouse Event Handlers
  const handleRuleMouseEnter = (index, textarea, button) => {
    initializeButtonHideTimeout(index);
    clearHideTimeout(index);
    showButton(textarea, button);
  };

  const handleRuleMouseLeave = (index, textarea, button) => {
    initializeButtonHideTimeout(index);
    hideButtonAfterDelay(index, textarea, button);
  };

  const handleButtonMouseEnter = (index, button) => {
    initializeButtonHideTimeout(index);
    clearHideTimeout(index);
    showButtonDirect(button);
  };

  const handleButtonMouseLeave = (index, textarea, button) => {
    initializeButtonHideTimeout(index);
    hideButtonAfterDelay(index, textarea, button);
  };

  // Utility Functions for Mouse Events
  const initializeButtonHideTimeout = (index) => {
    if (!buttonHideTimeoutsRef.current) {
      buttonHideTimeoutsRef.current = {};
    }
  };

  const clearHideTimeout = (index) => {
    if (buttonHideTimeoutsRef.current[index]) {
      clearTimeout(buttonHideTimeoutsRef.current[index]);
      buttonHideTimeoutsRef.current[index] = null;
    }
  };

  const showButton = (textarea, button) => {
    textarea.classList.add('text-shifted');
    button.style.left = '10px';
    button.style.opacity = '1';
    button.style.pointerEvents = 'auto';
  };

  const hideButtonAfterDelay = (index, textarea, button) => {
    buttonHideTimeoutsRef.current[index] = setTimeout(() => {
      textarea.classList.remove('text-shifted');
      button.style.left = '-90px';
      button.style.opacity = '0';
    }, 500);
  };

  const showButtonDirect = (button) => {
    button.style.opacity = '1';
    button.style.pointerEvents = 'auto';
  };

  // Function to fetch AI-generated summary
  const fetchAiSummary = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8080/api/v1/generate-audit-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          audit_results: auditResults,
        }),
      });
  
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
  
      const data = await response.json();
      setAiGeneratedSummary(data.report);
    } catch (error) {
      console.error('Error fetching AI summary:', error);
      setAiGeneratedSummary('Sorry, something went wrong.');
    }
  };

  const handleGenerateRule = async (index) => {
    let ruleText = rules[index].text;
  
    if (!ruleText.trim()) {
      console.log("Description cannot be empty");
      return;
    }
  
    try {
      const response = await fetch('http://127.0.0.1:8080/api/v1/rules/convert', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ description: ruleText }),
      });
  
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
  
      const data = await response.json();
  
      setRules((prevRules) =>
        prevRules.map((rule, i) => (i === index ? { ...rule, text: data.rule } : rule))
      );
    } catch (error) {
      console.error('Error generating rule:', error);
    }
  };

  // Debounced Functions
  const debouncedHandleNext = useDebounce(() => {
    if (sliderRef.current && activeStep < steps.length - 1) {
      setActiveStep((prevActiveStep) => prevActiveStep + 1);
      sliderRef.current.slickNext();
    }
  }, 50);

  const debouncedHandleBack = useDebounce(() => {
    if (sliderRef.current && activeStep > 0) {
      setActiveStep((prevActiveStep) => prevActiveStep - 1);
      sliderRef.current.slickPrev();
    }
  }, 50);

  // Handle Modal Close
  const handleModalClose = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8080/api/v1/audit/result');
      
      if (response.data.status === 'error') {
        console.error('Error fetching audit results:', response.data.error_message);
      } else {
        setAuditResults(response.data);
        setActiveStep(3);
        sliderRef.current.slickGoTo(3);
      }
    } catch (error) {
      console.error('Failed to fetch audit results:', error);
    }
  
    setOpenModal(false);
  };

  // Audit Process
  const startAuditProcess = () => {
    const stages = [1, 2, 3, 4];
    stages.forEach((stage, index) => {
      setTimeout(() => {
        setProgress(index < stages.length - 1 ? (index + 1) * 33 : 100);
        if (index === stages.length - 1) {
          setActiveStep(3);
        }
      }, index * 1000);
    });
  };

  // Menu Props
  const menuProps = {
    PaperProps: {
      style: {
        maxHeight: 300,
        overflowY: 'auto',
      },
    },
    MenuListProps: {
      disablePadding: true,
    },
    disableScrollLock: true,
  };

  // Progress Tracker Component
  const ProgressTracker = ({ progress }) => {
    const stages = ['Connecting', 'Executing', 'Analyzing', 'Done'];
    const activeStage = Math.floor(progress / (100 / stages.length));

    return (
      <Box className="progress-tracker">
        {stages.map((stage, index) => (
          <React.Fragment key={index}>
            <Box
              className={`progress-stage ${index <= activeStage ? 'active' : ''}`}
            >
              <Box
                className={`progress-dot ${index <= activeStage ? 'active-dot' : ''}`}
              />
              <Typography className={`progress-text ${index <= activeStage ? 'active-text' : ''}`}>
                {stage}
              </Typography>
            </Box>
            {index < stages.length - 1 && (
              <Box
                className={`progress-line ${index <= activeStage ? 'active-line' : ''}`}
                style={{ transitionDelay: index === activeStage - 1 ? '0.3s' : '0s' }}
              />
            )}
          </React.Fragment>
        ))}
      </Box>
    );
  };

  return (
    <div>

      <Box
        sx={{
          width: '70%',
          maxWidth: '1200px',
          p: 3,
          backgroundColor: 'gray.900',
          minHeight: '100vh',
          color: 'lightyellow',
          fontFamily: 'MonoLisa',
          position: 'relative',
          paddingBottom: '4rem',
          marginLeft: 'calc((100% - 70%) / 2 - 10px)',
        }}
      >
        <Stepper activeStep={activeStep} className="custom-stepper">
          {steps.map((label, index) => (
            <Step key={label}>
              <StepLabel
                StepIconProps={{
                  className: index === activeStep ? 'active-step-icon' : 'inactive-step-icon',
                }}
                className={`step-label ${
                  index < activeStep
                    ? 'completed-step-label'
                    : index === activeStep
                    ? 'active-step-label'
                    : 'upcoming-step-label'
                }`}
              >
                {label}
              </StepLabel>
            </Step>
          ))}
        </Stepper>

        <Slider {...sliderSettings} ref={sliderRef}>
          <Box className="information-box">
            <Typography
              variant="h6"
              component="div"
              className="information-title mono-lisa-font"
              sx={{ mb: 3 }}
            >
              Information
            </Typography>

            <Typography variant="body1" className="information-description mono-lisa-font" sx={{ mb: 2 }}>
              Enter the script information below.
            </Typography>

            {/* Script Name Input */}
            <div className="input-wrapper">
              <input
                type="text"
                className="custom-input mono-lisa-font"
                placeholder="Script Name"
                aria-label="Script Name"
                aria-describedby="basic-addon1"
                value={scriptName}
                onChange={(e) => setScriptName(e.target.value)}
              />
            </div>

            {/* Description Input */}
            <div className="input-wrapper">
              <input
                type="text"
                className="custom-input mono-lisa-font"
                placeholder="Description"
                aria-label="Description"
                aria-describedby="basic-addon2"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            {/* Rational Input */}
            <div className="input-wrapper">
              <input
                type="text"
                className="custom-input mono-lisa-font"
                placeholder="Rational"
                aria-label="Rational"
                value={rationale}
                onChange={(e) => setRationale(e.target.value)}
              />
            </div>

            {/* Mitigation Input */}
            <div className="input-wrapper">
              <input
                type="text"
                className="custom-input mono-lisa-font"
                placeholder="Mitigation"
                aria-label="Mitigation"
                value={mitigation}
                onChange={(e) => setMitigation(e.target.value)}
              />
            </div>

            {/* Detection Method Select */}
            <div className="input-wrapper">
              <FormControl fullWidth variant="outlined" className="flex-auto">
                <InputLabel id="detection-method-label" className="select-label mono-lisa-font">
                  Detection Method
                </InputLabel>
                <Select
                  labelId="detection-method-label"
                  id="detection-method"
                  label="Detection Method"
                  value={detectionMethod}
                  onChange={(e) => setDetectionMethod(e.target.value)}
                  onFocus={handleDropdownOpen}
                  onBlur={handleDropdownClose}
                  MenuProps={menuProps}
                  className="select-box mono-lisa-font"
                >
                  <MenuItem value="auto" className="select-item mono-lisa-font">Auto</MenuItem>
                  <MenuItem value="semi-auto" className="select-item mono-lisa-font">Semi-Auto</MenuItem>
                  <MenuItem value="manual" className="select-item mono-lisa-font">Manual</MenuItem>
                </Select>
              </FormControl>
            </div>

            {/* OS & Version Select */}
            <div className="input-wrapper">
              <FormControl fullWidth variant="outlined" className="flex-auto">
                <InputLabel id="os-version-label" className="select-label mono-lisa-font">
                  OS & Version
                </InputLabel>
                <Select
                  labelId="os-version-label"
                  id="os-version"
                  label="OS & Version"
                  value={osVersion}
                  onChange={(e) => setOsVersion(e.target.value)}
                  MenuProps={menuProps}
                  className="select-box mono-lisa-font"
                >
                  <MenuItem value="ubuntu22.04" className="select-item mono-lisa-font">Ubuntu 22.04</MenuItem>
                  <MenuItem value="windows10" className="select-item mono-lisa-font">Windows 10</MenuItem>
                </Select>
              </FormControl>
            </div>

            {/* Compliance Select */}
            <div className="input-wrapper">
              <FormControl fullWidth variant="outlined" className="flex-auto">
                <InputLabel id="compliance-label" className="select-label mono-lisa-font">
                  Compliance
                </InputLabel>
                <Select
                  labelId="compliance-label"
                  id="compliance"
                  label="Compliance"
                  value={complianceName}
                  onChange={(e) => setComplianceName(e.target.value)}
                  MenuProps={menuProps}
                  className="select-box mono-lisa-font"
                >
                  <MenuItem value="nist800-53r5" className="select-item mono-lisa-font">NIST 800-53r5</MenuItem>
                </Select>
              </FormControl>
            </div>

            {/* Control Select */}
            <div className="input-wrapper">
              <FormControl fullWidth variant="outlined" className="flex-auto">
                <InputLabel id="control-label" className="select-label mono-lisa-font">
                  Control
                </InputLabel>
                <Select
                  labelId="control-label"
                  id="control"
                  label="Control"
                  value={controlList}
                  onChange={(e) => setControlList([e.target.value])}
                  MenuProps={menuProps}
                  className="select-box mono-lisa-font"
                >
                  <MenuItem value="AC-3" className="select-item mono-lisa-font">AC-3</MenuItem>
                  <MenuItem value="AC-6" className="select-item mono-lisa-font">AC-6</MenuItem>
                  <MenuItem value="AC-7" className="select-item mono-lisa-font">AC-7</MenuItem>
                  <MenuItem value="AU-3" className="select-item mono-lisa-font">AU-3</MenuItem>
                  <MenuItem value="AU-4" className="select-item mono-lisa-font">AU-4</MenuItem>
                </Select>
              </FormControl>
            </div>
          </Box>

          <Box className="rule-page-box">
            <Typography
              variant="h6"
              component="div"
              className="rule-page-title mono-lisa-font"
              sx={{ mb: 3 }}
            >
              Rules
            </Typography>
            <Typography variant="body1" className="rule-page-description mono-lisa-font" sx={{ mb: 3 }}>
              Specify the rules for your script below.
            </Typography>

            {/* Condition Select */}
            <div className="condition-select-container mono-lisa-font">
              <FormControl
                fullWidth
                variant="outlined"
                className="condition-select"
              >
                <InputLabel id="condition-label" className="select-label mono-lisa-font">
                  Condition
                </InputLabel>
                <Select
                  labelId="condition-label"
                  id="condition"
                  label="Condition"
                  value={condition}
                  onChange={(e) => setCondition(e.target.value)}
                  MenuProps={menuProps}
                  className="select-box mono-lisa-font"
                >
                  <MenuItem value="any" className="select-item mono-lisa-font">Any</MenuItem>
                  <MenuItem value="none" className="select-item mono-lisa-font">None</MenuItem>
                  <MenuItem value="all" className="select-item mono-lisa-font">All</MenuItem>
                </Select>
              </FormControl>
            </div>

            {/* Rules Input */}
            <div className="rules-input-container">
              {rules.map((rule, index) => (
                <div key={index} className="rule-item-container">
                  <div className="rule-item">
                    <textarea
                      className={`rule-textarea ${rule.method === 'Using Natural Language' ? 'magicRule' : 'manualRule'}`}
                      placeholder={`Rule ${index + 1} (${rule.method})`}
                      aria-label={`Rule ${index + 1}`}
                      value={rule.text}
                      onChange={(e) => handleRuleChange(index, e.target.value)}
                      onMouseEnter={(e) => {
                        const textarea = e.currentTarget;
                        const button = textarea.parentNode.querySelector('.gen-rule-button');
                        if (textarea && button) {
                          handleRuleMouseEnter(index, textarea, button);
                        }
                      }}
                      onMouseLeave={(e) => {
                        const textarea = e.currentTarget;
                        const button = textarea.parentNode.querySelector('.gen-rule-button');
                        if (textarea && button) {
                          handleRuleMouseLeave(index, textarea, button);
                        }
                      }}
                    ></textarea>
                    {rule.method === 'Using Natural Language' && (
                      <button
                        type="button"
                        className="gradientButtonHovered gen-rule-button"
                        onClick={() => handleGenerateRule(index)}
                        onMouseEnter={(e) => {
                          const button = e.currentTarget;
                          handleButtonMouseEnter(index, button);
                        }}
                        onMouseLeave={(e) => {
                          const textarea = e.currentTarget.parentNode.querySelector('textarea');
                          const button = e.currentTarget;
                          handleButtonMouseLeave(index, textarea, button);
                        }}
                      >
                        Gen Rule
                      </button>
                    )}
                  </div>
                  {rules.length > 1 && (
                    <button
                      type="button"
                      className="delete-rule-button"
                      onClick={() => handleRemoveRule(index)}
                      title="Delete rule"
                    >
                      &times;
                    </button>
                  )}
                </div>
              ))}

              <div
                className="add-rule-container"
                onMouseEnter={handleActionButtonsMouseEnter}
                onMouseLeave={handleActionButtonsMouseLeave}
              >
                {isActionButtonsVisible ? (
                  <div className="action-buttons-container">
                    <button
                      type="button"
                      className="manualButton flex-1 mx-2"
                      onClick={handleAddManualRule}
                    >
                      Add Rule Manually
                    </button>
                    <button
                      type="button"
                      className={`gradientButton flex-1 mx-2 ${isAddButtonHovered ? 'gradientButtonHovered' : ''}`}
                      onClick={handleAddMagicRule}
                      onMouseEnter={() => setIsAddButtonHovered(true)}
                      onMouseLeave={() => setIsAddButtonHovered(false)}
                    >
                      Add Rule With GenAI
                    </button>
                  </div>
                ) : (
                  <button
                    type="button"
                    className="add-rule-button"
                    onMouseEnter={handleAddButtonMouseEnter}
                  >
                    +
                  </button>
                )}
              </div>
            </div>
          </Box>

          <Box className="target-system-page-box">
            <Typography variant="h6" component="div" className="target-system-page-title mono-lisa-font" sx={{ mb: 3 }}>
              Select Target System
            </Typography>

            <Typography variant="body1" className="target-system-page-description mono-lisa-font" sx={{ mb: 2 }}>
              In this step, enter the connection details for the target system you want to audit.<br />
              The system will connect to the target endpoint via SSH to perform the audit.
            </Typography>

            {/* Target System Name Input */}
            <div className="input-wrapper">
              <input
                type="text"
                className="custom-input mono-lisa-font"
                placeholder="Target System Name"
                aria-label="Target System Name"
                value={targetSystemName}
                onChange={(e) => setTargetSystemName(e.target.value)}
              />
            </div>

            {/* Target System Type Select */}
            <div className="input-wrapper mono-lisa-font">
              <FormControl fullWidth variant="outlined" className="custom-select mono-lisa-font">
                <InputLabel id="target-system-type-label" className="select-label mono-lisa-font">
                  Target System Type
                </InputLabel>
                <Select
                  labelId="target-system-type-label"
                  id="target-system-type"
                  value={targetSystemType}
                  onChange={handleSystemTypeChange}
                  label="Target System Type"
                  MenuProps={menuProps}
                  className="select-box mono-lisa-font"
                >
                  <MenuItem value="ubuntu18.04" className="select-item mono-lisa-font">Ubuntu 18.04</MenuItem>
                  <MenuItem value="ubuntu20.04" className="select-item mono-lisa-font">Ubuntu 20.04</MenuItem>
                  <MenuItem value="ubuntu22.04" className="select-item mono-lisa-font">Ubuntu 22.04</MenuItem>
                  <MenuItem value="windows10" className="select-item mono-lisa-font">Windows 10</MenuItem>
                  <MenuItem value="windows11" className="select-item mono-lisa-font">Windows 11</MenuItem>
                </Select>
              </FormControl>
            </div>

            {/* Port Input */}
            <div className="input-wrapper">
              <input
                type="text"
                className="custom-input"
                placeholder="Port"
                aria-label="Port"
                value={port}
                onChange={(e) => setPort(e.target.value)}
              />
            </div>

            {/* Username + IP Address Input */}
            <div className="input-group">
              <input
                type="text"
                className="custom-input"
                placeholder="Username"
                aria-label="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
              <span className="at-symbol">@</span>
              <input
                type="text"
                className="custom-input"
                placeholder="IP Address"
                aria-label="IP Address"
                value={ipAddress}
                onChange={(e) => setIpAddress(e.target.value)}
              />
            </div>

            {/* Password Input with Toggle Visibility */}
            <div className="password-input input-wrapper password-input-spacing">
              <input
                type={showPassword ? 'text' : 'password'}
                className="custom-input"
                placeholder="Password"
                aria-label="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                className="eye-icon"
                onClick={() => setShowPassword(!showPassword)}
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

          <Box className="audit-result-page-box">
            <Typography variant="h6" component="div" className="audit-result-page-title mono-lisa-font" sx={{ mb: 3 }}>
              {steps[3]}
            </Typography>
            <Typography variant="body1" className="audit-result-page-description mono-lisa-font" sx={{ mb: 3 }}>
              Below is the summary of the audit checks performed.
            </Typography>

            {/* Summary Table */}
            {auditResults && auditResults.scripts && auditResults.scripts[0] && (
              <Box className="audit-summary-box">
                {(() => {
                  const executionResultKey = Object.keys(auditResults.execution_results)[0];

                  return (
                    <table className="audit-summary-table">
                      <tbody>
                        <tr>
                          <td className="audit-summary-table-cell-left">
                            {auditResults.execution_results[executionResultKey].result.toUpperCase() === 'PASS' ? (
                              <Typography variant="h6" className="audit-pass-text">
                                (PASS) {auditResults.scripts[0].script_name}
                              </Typography>
                            ) : (
                              <Typography variant="h6" className="audit-fail-text">
                                (FAIL) {auditResults.scripts[0].script_name}
                              </Typography>
                            )}
                          </td>
                          <td className="audit-summary-table-cell-right">
                            <div className="pie-chart-container">
                              {(() => {
                                const ruleResults = auditResults.execution_results[executionResultKey].rule_results;
                                const passedCount = ruleResults.filter(result => result === true).length;
                                const failedCount = ruleResults.filter(result => result === false).length;

                                return (
                                  <PieChart width={200} height={250}>
                                    <Pie
                                      data={[
                                        { name: 'Passed', value: passedCount },
                                        { name: 'Failed', value: failedCount },
                                      ]}
                                      cx="50%"
                                      cy="45%"
                                      labelLine={false}
                                      outerRadius={80}
                                      fill="#8884d8"
                                      dataKey="value"
                                    >
                                      <Cell key="cell-0" fill="#00C49F" />
                                      <Cell key="cell-1" fill="lightcoral" />
                                    </Pie>
                                    <Tooltip formatter={(value, name) => `${name}: ${value}`} />
                                    <Legend
                                      layout="horizontal"
                                      align="center"
                                      verticalAlign="bottom"
                                      iconType="circle"
                                      wrapperStyle={{
                                        marginTop: 10,
                                        fontSize: '12px',
                                        color: 'lightyellow',
                                      }}
                                    />
                                  </PieChart>
                                );
                              })()}
                            </div>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  );
                })()}
              </Box>
            )}

            {/* GenAI Audit Summary Table */}
            {auditResults && (
              <Box className="audit-genai-summary-box">
                <table className="audit-genai-summary-table">
                  <thead>
                    <tr>
                      <th colSpan="2" className="genai-summary-header">
                        GenAI Audit Summary
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td colSpan="2" className="genai-summary-content">
                        <Typography variant="body1" className="mono-lisa-font">
                          <StyledMarkdown>
                            <ReactMarkdown>{aiGeneratedSummary || 'Loading AI summary...'}</ReactMarkdown>
                          </StyledMarkdown>
                        </Typography>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </Box>
            )}

            {/* Script Information Table */}
            {auditResults && auditResults.scripts && auditResults.scripts[0] && (
              <Box className="script-info-box">
                <table className="script-info-table">
                  <thead>
                    <tr>
                      <th colSpan="2" className="script-info-header">
                        Script Information
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {/* Repeat for each table row, using corresponding CSS classes */}
                    <tr>
                      <td className="script-info-cell-bold">Script Name</td>
                      <td className="script-info-cell">{auditResults.scripts[0].script_name}</td>
                    </tr>
                    <tr>
                      <td className="script-info-cell-bold">Description</td>
                      <td className="script-info-cell">{auditResults.scripts[0].description}</td>
                    </tr>
                    <tr>
                      <td className="script-info-cell-bold">Rationale</td>
                      <td className="script-info-cell">{auditResults.scripts[0].rationale}</td>
                    </tr>
                    <tr>
                      <td className="script-info-cell-bold">Mitigation</td>
                      <td className="script-info-cell">{auditResults.scripts[0].mitigation}</td>
                    </tr>
                    <tr>
                      <td className="script-info-cell-bold">Detection Method</td>
                      <td className="script-info-cell">{auditResults.scripts[0].detection_method}</td>
                    </tr>
                    <tr>
                      <td className="script-info-cell-bold">OS Version</td>
                      <td className="script-info-cell">{auditResults.scripts[0].os_version}</td>
                    </tr>
                  </tbody>
                </table>
              </Box>
            )}

            {/* Automation Audit Results Table */}
            {auditResults && auditResults.scripts && auditResults.scripts[0] && (
              <Box className="automation-results-box">
                <table className="automation-results-table">
                  <thead>
                    <tr>
                      <th className="automation-results-header">#</th>
                      <th className="automation-results-header">
                        {`Rule (${auditResults.execution_results[Object.keys(auditResults.execution_results)[0]].condition})`}
                      </th>
                      <th className="automation-results-header">Result</th>
                    </tr>
                  </thead>
                  <tbody>
                    {auditResults.scripts[0].rules.map((rule, index) => {
                      const executionResultKey = Object.keys(auditResults.execution_results)[0];
                      const isPass = auditResults.execution_results[executionResultKey].rule_results[index];

                      return (
                        <tr key={index}>
                          <td className="automation-results-cell-center">{index + 1}</td>
                          <td className="automation-results-cell-left">{rule}</td>
                          <td className={`automation-results-cell-center ${isPass ? 'text-pass' : 'text-fail'}`}>
                            {isPass ? 'Pass' : 'Fail'}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </Box>
            )}

            {/* Endpoint Information Table */}
            {auditResults && auditResults.ssh_info && (
              <Box className="endpoint-info-box">
                <table className="endpoint-info-table">
                  <thead>
                    <tr>
                      <th colSpan="2" className="endpoint-info-header">
                        Endpoint Information
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {/* Repeat for each table row, using corresponding CSS classes */}
                    <tr>
                      <td className="endpoint-info-cell-bold">Target System Name</td>
                      <td className="endpoint-info-cell">{auditResults.ssh_info.target_system_name}</td>
                    </tr>
                    <tr>
                      <td className="endpoint-info-cell-bold">Target System Type</td>
                      <td className="endpoint-info-cell">{auditResults.ssh_info.target_system_type}</td>
                    </tr>
                    <tr>
                      <td className="endpoint-info-cell-bold">Port</td>
                      <td className="endpoint-info-cell">{auditResults.ssh_info.port}</td>
                    </tr>
                    <tr>
                      <td className="endpoint-info-cell-bold">Username</td>
                      <td className="endpoint-info-cell">{auditResults.ssh_info.username}</td>
                    </tr>
                    <tr>
                      <td className="endpoint-info-cell-bold">IP</td>
                      <td className="endpoint-info-cell">{auditResults.ssh_info.ip}</td>
                    </tr>
                  </tbody>
                </table>
              </Box>
            )}
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
            left: '50%', // Initial position relative to the screen
            transform: 'translateX(-45.5%)', // Horizontal adjustment for the entire container
            width: '100%',
            maxWidth: '1200px',
            display: 'flex',
            justifyContent: 'center', // Center the grid container horizontally
            zIndex: 10,
          }}
        >
          <Grid
            container
            sx={{
              width: 'auto', // Allow the grid to auto-adjust its width based on content
              transform: 'translateX(-10%)', // Adjust the position of the entire grid container
              justifyContent: 'space-between', // Ensure space is distributed evenly
              alignItems: 'center', // Align items in the center vertically
            }}
          >
            <Grid item> {/* No fixed width to let the button adjust to its text */}
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
                  whiteSpace: 'nowrap', // Prevent button from expanding unnecessarily
                  '&:hover': {
                    transform: 'scale(1.05)',
                    backgroundColor: '#ffd700',
                    color: 'lightyellow',
                  },
                }}
              >
                Back
              </Button>
            </Grid>

            <Grid item sx={{ width: '975px' }}> {/* Adjust this width to control space between buttons */}
            </Grid>

            <Grid item> {/* No fixed width to let the button adjust to its text */}
              {activeStep < steps.length - 1 ? (
                <Button
                  variant="contained"
                  color="primary"
                  onClick={activeStep === 2 ? handleAudit : handleNext} // Attach handleAudit for the Audit step
                  sx={{
                    transition: 'transform 0.3s',
                    fontFamily: 'MonoLisa',
                    backgroundColor: '#1976d2',
                    color: 'lightyellow',
                    whiteSpace: 'nowrap', // Prevent button from expanding unnecessarily
                    '&:hover': {
                      transform: 'scale(1.05)',
                      backgroundColor: '#ffd700',
                      color: 'lightyellow',
                    },
                  }}
                >
                  {activeStep === 2 ? 'Audit' : 'Next!'}
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
                    whiteSpace: 'nowrap', // Prevent button from expanding unnecessarily
                    '&:hover': {
                      transform: 'scale(1.05)',
                      backgroundColor: '#ffd700',
                      color: 'lightyellow',
                    },
                  }}
                >
                  Replay
                </Button>
              )}
            </Grid>
          </Grid>
        </Box>

      </Box>
      <FloatingChat />
    </div>
  );
};

export default PrototypePage;
