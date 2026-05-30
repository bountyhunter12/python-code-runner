import { useState, useRef } from 'react'
import Editor from '@monaco-editor/react'

// Default Python code to display on load
const DEFAULT_CODE = `# Welcome to Python Code Runner!
# Write your Python code below and click "Run" to execute it.

print("Hello, world!")

# Try some examples:
# 1. Simple calculation
result = 2 ** 10
print(f"2 to the power of 10 is: {result}")

# 2. A simple list
numbers = [1, 2, 3, 4, 5]
print(f"Sum of {numbers} = {sum(numbers)}")

# 3. A loop
for i in range(5):
    print(f"Count: {i}")
`

function App() {
  const [code, setCode] = useState(DEFAULT_CODE)
  const [output, setOutput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [executionStats, setExecutionStats] = useState(null)
  const [error, setError] = useState(null)
  const editorRef = useRef(null)

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor
    // Configure Python language
    monaco.editor.setModelLanguage(editor.getModel(), 'python')
  }

  const handleRunCode = async () => {
    setIsLoading(true)
    setOutput('')
    setError(null)
    setExecutionStats(null)

    try {
      const response = await fetch('/api/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code }),
      })

      const data = await response.json()

      if (!response.ok) {
        const errorMsg = data.detail?.message || data.detail?.error || 'Unknown error'
        setError(errorMsg)
        return
      }

      // Build output string
      let outputText = ''
      if (data.stdout) {
        outputText += data.stdout
      }
      if (data.stderr) {
        if (outputText) outputText += '\n'
        outputText += data.stderr
      }
      if (!outputText) {
        outputText = '(No output)'
      }

      setOutput(outputText)
      setExecutionStats({
        exitCode: data.exit_code,
        timeMs: data.time_ms
      })
    } catch (err) {
      setError('Failed to connect to the server. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleClearOutput = () => {
    setOutput('')
    setError(null)
    setExecutionStats(null)
  }

  const handleClearEditor = () => {
    setCode('')
  }

  const handleResetCode = () => {
    setCode(DEFAULT_CODE)
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-left">
          <span className="logo">🐍 Python Code Runner</span>
        </div>
        <div className="header-right">
          <button
            className="btn btn-secondary"
            onClick={handleResetCode}
            title="Reset to default code"
          >
            Reset
          </button>
          <button
            className="btn btn-primary"
            onClick={handleRunCode}
            disabled={isLoading || !code.trim()}
          >
            {isLoading ? (
              <>
                <span className="spinner"></span>
                Running...
              </>
            ) : (
              <>
                <span>▶</span>
                Run Code
              </>
            )}
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {/* Editor Section */}
        <div className="editor-section">
          <div className="editor-header">
            <div className="editor-tabs">
              <span className="editor-tab active">
                <span style={{ marginRight: '6px' }}>📄</span>
                main.py
              </span>
            </div>
          </div>
          <div className="editor-container">
            <Editor
              height="100%"
              defaultLanguage="python"
              theme="vs-dark"
              value={code}
              onChange={(value) => setCode(value || '')}
              onMount={handleEditorDidMount}
              options={{
                fontSize: 14,
                fontFamily: "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                padding: { top: 16 },
                lineNumbers: 'on',
                renderLineHighlight: 'line',
                automaticLayout: true,
                tabSize: 4,
                wordWrap: 'on',
              }}
            />
          </div>
        </div>

        {/* Output Section */}
        <div className="output-section">
          <div className="output-header">
            <span className="output-title">Output</span>
            {executionStats && (
              <div className="output-stats">
                <span className="stat">
                  Exit:
                  <span className={`stat-value ${executionStats.exitCode === 0 ? 'success' : 'error'}`}>
                    {executionStats.exitCode}
                  </span>
                </span>
                <span className="stat">
                  Time:
                  <span className="stat-value">{executionStats.timeMs}ms</span>
                </span>
              </div>
            )}
            {(output || error) && (
              <button className="btn btn-clear" onClick={handleClearOutput}>
                Clear
              </button>
            )}
          </div>
          <div className="output-content">
            {error ? (
              <div className="stderr">{error}</div>
            ) : output ? (
              output
            ) : (
              <span className="no-output">
                Run your code to see output here...
              </span>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default App