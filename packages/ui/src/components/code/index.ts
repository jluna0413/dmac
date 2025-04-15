/**
 * Code Components
 */
import React from 'react';
import { Box, Paper, Typography } from '@mui/material';

export interface CodeBlockProps {
  code: string;
  language?: string;
}

/**
 * Code block component
 */
export const CodeBlock: React.FC<CodeBlockProps> = ({ code, language = 'typescript' }) => {
  return (
    <Paper
      elevation={1}
      sx={{
        p: 2,
        my: 2,
        borderRadius: 1,
        backgroundColor: 'grey.900',
        overflow: 'auto',
      }}
    >
      <pre style={{ margin: 0 }}>
        <code className={`language-${language}`}>{code}</code>
      </pre>
    </Paper>
  );
};

export interface CodeEditorProps {
  code: string;
  language?: string;
  onChange?: (code: string) => void;
  readOnly?: boolean;
}

/**
 * Code editor component
 */
export const CodeEditor: React.FC<CodeEditorProps> = ({
  code,
  language = 'typescript',
  onChange,
  readOnly = false,
}) => {
  // This is a placeholder for a real code editor component
  // In a real implementation, you would use a library like Monaco Editor or CodeMirror
  return (
    <Box
      sx={{
        border: '1px solid',
        borderColor: 'grey.300',
        borderRadius: 1,
        p: 2,
        backgroundColor: 'grey.900',
        color: 'grey.100',
        fontFamily: 'monospace',
        fontSize: '0.875rem',
        overflow: 'auto',
        minHeight: '200px',
      }}
    >
      <Typography component="pre" sx={{ margin: 0 }}>
        <code className={`language-${language}`}>{code}</code>
      </Typography>
    </Box>
  );
};
