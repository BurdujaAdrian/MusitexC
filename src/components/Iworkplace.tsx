import React, { useState, useEffect, useRef } from 'react';
import { Camera, GripVertical, ArrowLeft, Save } from 'lucide-react';
import MusicStaffRenderer from './MusicStaffRenderer';
import ProjectService from './services/ProjectService';
import AccountDropdown from './AccountDropdown';
import ExportDropdown from './ExportDropdown';

// TypeScript interfaces
interface ParseResult {
    hasError: boolean;
    errorLine: number;
    errorMessage: string;
    sheetMusicImage: string | null;
}

interface IWorkplaceProps {
    onNavigateToDashboard: () => void;
    projectId?: string;
}

// Custom hook for smooth resizing
const useResizer = (initialWidth: number = 50) => {
    const [editorWidth, setEditorWidth] = useState(initialWidth);
    const isDragging = useRef(false);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            if (!isDragging.current || !containerRef.current) return;

            const container = containerRef.current;
            const containerRect = container.getBoundingClientRect();
            const containerWidth = containerRect.width;

            // Calculate new width as percentage
            let newWidth = ((e.clientX - containerRect.left) / containerWidth) * 100;

            // Limit between 20% and 80%
            newWidth = Math.max(20, Math.min(80, newWidth));

            setEditorWidth(newWidth);
        };

        const handleMouseUp = () => {
            isDragging.current = false;
            document.body.style.cursor = 'default';
            document.body.style.userSelect = 'auto';
        };

        const handleMouseDown = (e: MouseEvent) => {
            if ((e.target as HTMLElement).closest('.resizer-handle')) {
                e.preventDefault();
                isDragging.current = true;
                document.body.style.cursor = 'col-resize';
                document.body.style.userSelect = 'none';
            }
        };

        // Add event listeners to document
        document.addEventListener('mousedown', handleMouseDown);
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
        document.addEventListener('mouseleave', handleMouseUp);

        // Cleanup
        return () => {
            document.removeEventListener('mousedown', handleMouseDown);
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
            document.removeEventListener('mouseleave', handleMouseUp);
        };
    }, []);

    return { editorWidth, containerRef };
};

const IWorkplace: React.FC<IWorkplaceProps> = ({ onNavigateToDashboard, projectId }) => {
    const [projectTitle, setProjectTitle] = useState('Untitled Project');
    const [code, setCode] = useState('// Write your Music DSL code here\n\nplay C4 D4 E4 F4 G4 A4 B4 C5');
    const [originalCode, setOriginalCode] = useState(code);
    const [originalTitle, setOriginalTitle] = useState(projectTitle);
    const [parseResult, setParseResult] = useState<ParseResult>({
        hasError: false,
        errorLine: -1,
        errorMessage: '',
        sheetMusicImage: null
    });
    const [theme, setTheme] = useState<'light' | 'dark'>('light');
    const [isLoading, setIsLoading] = useState(false);
    const [isSaved, setIsSaved] = useState(true);
    const { editorWidth, containerRef } = useResizer(50);

    // Account dropdown handlers
    const handleLogout = () => {
        // Navigate to login page or clear authentication
        window.location.href = '/login';
    };

    const handleSettings = () => {
        alert('Account settings would be implemented here');
        // In a real app, you would navigate to the settings page
    };

    // Export handlers
    const handleExportPDF = () => {
        // Placeholder for PDF export functionality
        console.log('Exporting as PDF...');
        alert('PDF export functionality will be implemented here');
    };

    const handleExportMIDI = () => {
        // Placeholder for MIDI export functionality
        console.log('Exporting as MIDI...');
        alert('MIDI export functionality will be implemented here');
    };

    // Load project on mount if projectId is provided
    useEffect(() => {
        if (projectId) {
            const project = ProjectService.getProjectById(projectId);
            if (project) {
                setProjectTitle(project.title);
                setCode(project.content);
                // Store original values to compare against
                setOriginalCode(project.content);
                setOriginalTitle(project.title);
                setIsSaved(true);
            }
        } else {
            // Create a new project
            const newProject = ProjectService.createProject('Untitled Project', code);
            setProjectTitle(newProject.title);
            // Store original values to compare against
            setOriginalCode(code);
            setOriginalTitle(newProject.title);
            setIsSaved(true);
        }
    }, [projectId]);

    // Track changes and update saved state
    useEffect(() => {
        // Only mark as unsaved if content has actually changed
        const contentChanged = code !== originalCode || projectTitle !== originalTitle;
        setIsSaved(!contentChanged);
    }, [code, projectTitle, originalCode, originalTitle]);

    // This would be replaced with actual API call to your Python backend
    const processCode = async (codeToProcess: string) => {
        setIsLoading(true);

        // Simulating API call to Python backend
        try {
            // Mock backend response - in reality, this would come from your Python service
            await new Promise(resolve => setTimeout(resolve, 300)); // Simulate network delay

            const mockResponse: ParseResult = {
                hasError: codeToProcess.includes('error'),
                errorLine: codeToProcess.includes('error')
                    ? codeToProcess.split('\n').findIndex(line => line.includes('error'))
                    : -1,
                errorMessage: codeToProcess.includes('error') ? 'Syntax error in note sequence' : '',
                // In reality, this could be a base64 image string of rendered sheet music from your Python backend
                sheetMusicImage: !codeToProcess.includes('error')
                    ? 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Music-staff.svg/640px-Music-staff.svg.png'
                    : null
            };

            setParseResult(mockResponse);
        } catch (error) {
            setParseResult({
                hasError: true,
                errorLine: -1,
                errorMessage: 'Failed to communicate with the music compiler service',
                sheetMusicImage: null
            });
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        // Parse code whenever it changes (with debounce)
        const timer = setTimeout(() => {
            processCode(code);
        }, 500);

        return () => clearTimeout(timer);
    }, [code]);

    // Handle code changes
    const handleCodeChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setCode(e.target.value);
    };

    // Handle title changes
    const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setProjectTitle(e.target.value);
    };

    // Toggle theme
    const toggleTheme = () => {
        setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
    };

    // Run the code manually
    const handleRunCode = () => {
        processCode(code);
    };

    // Save the code
    const handleSaveCode = () => {
        if (projectId) {
            ProjectService.updateProject(projectId, {
                title: projectTitle,
                content: code
            });
            // Update the original values after saving
            setOriginalCode(code);
            setOriginalTitle(projectTitle);
            setIsSaved(true);
        } else {
            // Create new project if somehow we don't have an ID
            const newProject = ProjectService.createProject(projectTitle, code);
            // Update the original values after saving
            setOriginalCode(code);
            setOriginalTitle(projectTitle);
            setIsSaved(true);
        }
    };

    // Navigate back to dashboard with confirmation if unsaved
    const handleNavigateBack = () => {
        if (!isSaved) {
            const confirmLeave = window.confirm('You have unsaved changes. Are you sure you want to leave?');
            if (!confirmLeave) {
                return;
            }
        }
        onNavigateToDashboard();
    };

    // Generate line numbers for the editor
    const lineNumbers = code.split('\n').map((_, index) => (
        <div
            key={index}
            className={`text-right pr-2 select-none ${
                parseResult && parseResult.errorLine === index ? 'bg-red-200' : ''
            }`}
        >
            {index + 1}
        </div>
    ));

    // Define CSS for our component
    const styles = {
        container: `flex flex-col h-screen ${theme === 'dark' ? 'bg-gray-800 text-white' : 'bg-gray-100 text-black'}`,
        toolbar: `p-2 border-b ${theme === 'dark' ? 'border-gray-700 bg-gray-900' : 'border-gray-300 bg-gray-200'} flex justify-between items-center`,
        mainContent: 'flex flex-1 overflow-hidden relative',
        editorPanel: `flex flex-col ${theme === 'dark' ? 'bg-gray-900' : 'bg-white'} border-r ${theme === 'dark' ? 'border-gray-700' : 'border-gray-300'}`,
        editorHeader: 'p-2 border-b text-sm font-medium flex justify-between items-center',
        lineNumbers: `py-2 text-xs ${theme === 'dark' ? 'bg-gray-800 text-gray-500' : 'bg-gray-100 text-gray-600'}`,
        codeEditor: `flex-1 p-2 text-sm font-mono outline-none resize-none ${theme === 'dark' ? 'bg-gray-900 text-gray-300' : 'bg-white'}`,
        problemsPanel: `p-2 ${theme === 'dark' ? 'bg-gray-800' : 'bg-gray-100'} text-sm max-h-28 overflow-auto border-t ${theme === 'dark' ? 'border-gray-700' : 'border-gray-300'}`,
        previewPanel: `overflow-auto ${theme === 'dark' ? 'bg-gray-800' : 'bg-gray-50'}`,
        statusBar: `px-4 py-1 text-xs ${theme === 'dark' ? 'bg-gray-900 text-gray-400' : 'bg-gray-200 text-gray-600'} flex justify-between`,
    };

    return (
        <div
            ref={containerRef}
            className={styles.container}
        >
            {/* Toolbar */}
            <div className={styles.toolbar}>
                <div className="flex items-center space-x-4">
                    <button
                        onClick={handleNavigateBack}
                        className="flex items-center text-gray-600 hover:text-gray-800"
                    >
                        <ArrowLeft size={18} />
                        <span className="ml-1">Back to Projects</span>
                    </button>

                    <div className="flex items-center space-x-2">
                        <Camera size={24} />
                        <input
                            type="text"
                            value={projectTitle}
                            onChange={handleTitleChange}
                            className={`text-lg font-bold bg-transparent border ${isSaved ? 'border-transparent' : 'border-yellow-400'} focus:border-blue-500 focus:outline-none px-1 rounded`}
                        />
                    </div>
                </div>
                <div className="flex items-center space-x-4">
                    <button
                        onClick={toggleTheme}
                        className={`px-2 py-1 rounded ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-300'}`}
                    >
                        {theme === 'light' ? 'Dark Mode' : 'Light Mode'}
                    </button>
                    <button
                        onClick={handleRunCode}
                        className={`px-2 py-1 rounded ${theme === 'dark' ? 'bg-blue-600' : 'bg-blue-500'} text-white`}
                    >
                        Run
                    </button>
                    <button
                        onClick={handleSaveCode}
                        className={`px-2 py-1 rounded flex items-center ${isSaved
                            ? (theme === 'dark' ? 'bg-gray-700 text-gray-400' : 'bg-gray-300 text-gray-500')
                            : (theme === 'dark' ? 'bg-green-600 text-white' : 'bg-green-500 text-white')
                        }`}
                        disabled={isSaved}
                    >
                        <Save size={16} className="mr-1" />
                        <span>{isSaved ? 'Saved' : 'Save'}</span>
                    </button>
                    <ExportDropdown
                        onExportPDF={handleExportPDF}
                        onExportMIDI={handleExportMIDI}
                        theme={theme}
                    />
                    <AccountDropdown
                        onLogout={handleLogout}
                        onSettings={handleSettings}
                    />
                </div>
            </div>

            {/* Main content with resizable panels */}
            <div className={styles.mainContent}>
                {/* Code editor side */}
                <div
                    className={styles.editorPanel}
                    style={{ width: `${editorWidth}%` }}
                >
                    <div className={styles.editorHeader}>
                        <span>main.mdsl</span>
                        <div className="text-xs">
                            {parseResult.hasError ? (
                                <span className="text-red-500">● 1 Error</span>
                            ) : (
                                <span className="text-green-500">✓ No Errors</span>
                            )}
                        </div>
                    </div>

                    <div className="flex flex-1 overflow-auto">
                        {/* Line numbers */}
                        <div className={styles.lineNumbers}>
                            {lineNumbers}
                        </div>

                        {/* Code editor */}
                        <textarea
                            value={code}
                            onChange={handleCodeChange}
                            className={styles.codeEditor}
                            spellCheck={false}
                        />
                    </div>

                    {/* Problems panel */}
                    {parseResult.hasError && (
                        <div className={styles.problemsPanel}>
                            <div className="font-medium mb-1">Problems</div>
                            <div className="flex items-start">
                                <div className="text-red-500 mr-2">●</div>
                                <div>
                                    <div className="font-medium">{parseResult.errorMessage}</div>
                                    <div className={`text-xs ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
                                        main.mdsl:line {parseResult.errorLine + 1}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Resizer handle */}
                <div
                    className="resizer-handle"
                    style={{
                        position: 'absolute',
                        top: 0,
                        bottom: 0,
                        left: `${editorWidth}%`,
                        transform: 'translateX(-50%)',
                        width: '12px',
                        cursor: 'col-resize',
                        backgroundColor: 'transparent',
                        border: 'none',
                        zIndex: 10,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(59, 130, 246, 0.1)'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                >
                    <div style={{
                        width: '2px',
                        height: '100%',
                        backgroundColor: theme === 'dark' ? '#374151' : '#e5e7eb',
                        position: 'relative',
                    }}>
                        <GripVertical
                            className="text-gray-400 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
                            size={16}
                        />
                    </div>
                </div>

                {/* Sheet music side */}
                <div
                    className={styles.previewPanel}
                    style={{ width: `${100 - editorWidth}%` }}
                >
                    <div className="p-4">
                        <div className="border-b border-gray-300 pb-2 mb-4">
                            <h2 className="text-xl font-semibold">Sheet Music Preview</h2>
                        </div>

                        <div className="bg-white p-4 rounded shadow">
                            <MusicStaffRenderer
                                code={code}
                                hasError={parseResult.hasError}
                                isLoading={isLoading}
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* Status bar */}
            <div className={styles.statusBar}>
                <div>Music DSL Editor v1.0</div>
                <div className="flex items-center">
                    {isLoading ? 'Processing...' : parseResult.hasError ? '1 Error' : 'Ready'}
                    {!isSaved &&
                        <span className="ml-2 text-yellow-500">●</span>
                    }
                </div>
            </div>
        </div>
    );
};

export default IWorkplace;