"""
Error handling utilities for DTI CPMS deployment issues
"""

import streamlit as st
import os

def show_js_error_recovery():
    """Show error recovery page for JavaScript module issues"""
    st.error("**Application Loading Issue Detected**")
    
    st.markdown("""
    ### What happened?
    There was an issue loading some application components. This can happen due to:
    - Network connectivity issues
    - Browser cache conflicts
    - Server deployment updates
    
    ### Quick Solutions:
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("**Refresh Page**", use_container_width=True):
            st.javascript("window.location.reload(true);")
    
    with col2:
        if st.button("**Clear Cache**", use_container_width=True):
            st.javascript("""
                if ('caches' in window) {
                    caches.keys().then(function(names) {
                        names.forEach(function(name) {
                            caches.delete(name);
                        });
                    });
                }
                setTimeout(function() { 
                    window.location.reload(true); 
                }, 1000);
            """)
    
    with col3:
        if st.button("**Go Home**", use_container_width=True):
            st.javascript("window.location.href = '/';")
    
    st.markdown("---")
    
    with st.expander("**Advanced Troubleshooting**"):
        st.markdown("""
        **For IT Support:**
        
        1. **Clear Browser Data:**
           - Press `Ctrl+Shift+Delete` (Chrome/Edge) or `Ctrl+Shift+Del` (Firefox)
           - Select "Cached images and files"
           - Click "Clear data"
        
        2. **Try Incognito/Private Mode:**
           - Press `Ctrl+Shift+N` (Chrome/Edge) or `Ctrl+Shift+P` (Firefox)
           - Access the application in private mode
        
        3. **Check Network Connection:**
           - Ensure stable internet connectivity
           - Try refreshing in a few minutes
        
        4. **Contact Support:**
           - If issue persists, contact your IT administrator
           - Reference Error: "Failed to fetch dynamically imported module"
        """)
    
    # Add automatic retry mechanism
    st.markdown("""
    <script>
    // Automatic retry after 30 seconds
    setTimeout(function() {
        console.log('Auto-retry attempt...');
        window.location.reload(true);
    }, 30000);
    </script>
    """, unsafe_allow_html=True)

def check_js_module_error():
    """Check if there's a JavaScript module error and show recovery page"""
    # This would be called from main modules to handle JS errors gracefully
    if os.getenv('RENDER') and 'js_error' in st.session_state:
        show_js_error_recovery()
        return True
    return False
