/**
 * Button Components
 */
import React from 'react';
import { Button as MuiButton, ButtonProps as MuiButtonProps } from '@mui/material';

export interface ButtonProps extends MuiButtonProps {
  variant?: 'contained' | 'outlined' | 'text';
  color?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
  size?: 'small' | 'medium' | 'large';
}

/**
 * Primary button component
 */
export const Button: React.FC<ButtonProps> = (props) => {
  return <MuiButton {...props} />;
};

/**
 * Icon button component
 */
export const IconButton: React.FC<ButtonProps> = (props) => {
  return <MuiButton {...props} />;
};

/**
 * Action button component
 */
export const ActionButton: React.FC<ButtonProps> = (props) => {
  const { children, ...rest } = props;
  return (
    <MuiButton
      variant="contained"
      color="primary"
      {...rest}
    >
      {children}
    </MuiButton>
  );
};
