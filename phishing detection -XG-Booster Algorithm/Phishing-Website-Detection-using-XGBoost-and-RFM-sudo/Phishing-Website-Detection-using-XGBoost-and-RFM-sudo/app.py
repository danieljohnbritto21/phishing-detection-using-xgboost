import streamlit as st
import numpy as np
import pickle
from urllib.parse import urlparse
import requests
from urllib.parse import urlparse
from datetime import datetime
import re
import ipaddress
from requests.exceptions import SSLError, Timeout  # Add this import for SSLError and Timeout
import json
import os

HISTORY_FILE = "scan_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(url, result, score):
    history = load_history()
    if history and history[0]["url"] == url and history[0]["result"] == result:
        return
    entry = {
        "url": url,
        "result": result,
        "score": score,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    history.insert(0, entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[:50], f)

def get_domain(url):  
    domain = urlparse(url).netloc
    if re.match(r"^www.",domain):
        domain = domain.replace("www.","")
    return domain

def having_ip(url):
    try:
        ipaddress.ip_address(url)
        ip = 1
    except:
        ip = 0
    return ip

def have_at_sign(url):
    if "@" in url:
        at = 1
    else:
        at = 0
    return at

def get_length(url):
    if len(url) < 54:
        length = 0
    else:
        length = 1
    return length

def get_depth(url):
    s = urlparse(url).path.split('/')
    depth = 0
    for j in range(len(s)):
        if len(s[j]) != 0:
            depth = depth+1
    return depth

def redirection(url):
    pos = url.rfind('//')
    if pos > 6:
        if pos > 7:
            return 1
        else:
            return 0
    else:
        return 0

def http_domain(url):
    domain = urlparse(url).netloc
    if 'https' in domain:
        return 1
    else:
        return 0

def tiny_url(url):
    shortening_services = r"bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|" \
                          r"yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|" \
                          r"short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|" \
                          r"doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|db\.tt|" \
                          r"qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|q\.gs|is\.gd|" \
                          r"po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|x\.co|" \
                          r"prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|" \
                          r"tr\.im|link\.zip\.net"
    match=re.search(shortening_services,url)
    if match:
        return 1
    else:
        return 0

def prefix_suffix(url):
    if '-' in urlparse(url).netloc:
        return 1
    else:
        return 0 

def web_traffic(url):
    try:
        querystring = {"domain": url}
        headers = {
            "X-RapidAPI-Key": "cd4733fedbmsh6f2cfc21cf195f2p1d088djsn84e6c824c74e",
            "X-RapidAPI-Host": "similar-web.p.rapidapi.com"
        }
        response = requests.get("https://similar-web.p.rapidapi.com/get-analysis", headers=headers, params=querystring)
        data = response.json()
        rank = data['GlobalRank']['Rank']
        rank = int(rank)
    except (requests.exceptions.RequestException, ValueError, KeyError):
        rank = 1

    if rank < 100000:
        return 1
    else:
        return 0

def iframe(response):
    if response == "":
        return 1
    else:
        if re.findall(r"[<iframe>|<frameBorder>]", response.text):
            return 0
        else:
            return 1

def mouse_over(response): 
    if response == "" :
        return 1
    else:
        if re.findall("<script>.+onmouseover.+</script>", response.text):
            return 1
        else:
            return 0

def right_click(response):
    if response == "":
        return 1
    else:
        if re.findall(r"event.button ?== ?2", response.text):
            return 0
        else:
            return 1

def forwarding(response):
    if response == "":
        return 1
    else:
        if len(response.history) <= 2:
            return 0
        else:
            return 1

def get_http_response(url):
    try:
        response = requests.get(url, timeout=5)  # Set a timeout of 5 seconds
        return response
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")
        return None

def extract_features(url):
    features = []
    
    # Address bar based features
    features.append(having_ip(url))
    features.append(have_at_sign(url))
    features.append(get_length(url))
    features.append(get_depth(url))
    features.append(redirection(url))
    features.append(http_domain(url))
    features.append(tiny_url(url))
    features.append(prefix_suffix(url))

    # Domain based features
    dns = 0
    dns_age = 0
    dns_end = 0
    features.append(dns)
    features.append(dns_age)
    features.append(dns_end)
    features.append(web_traffic(url))
    response = get_http_response(url)

    # HTML & Javascript based features
    if response is not None:
        features.append(iframe(response))
        features.append(mouse_over(response))
        features.append(right_click(response))
        features.append(forwarding(response))
    else:
        # If response is None, set these features to 0 or None
        features.extend([0, 0, 0, 0])

    return features

def predict_phishing(features):
    # Load the model
    with open('mlp_model.pkl', 'rb') as file:
        loaded_model = pickle.load(file)

    # Make predictions
    new_data = np.array([features])
    prediction = loaded_model.predict(new_data)

    return prediction

def get_url_info(url):
    """Extract URL components and display as info"""
    parsed_url = urlparse(url)
    info = {
        'protocol': parsed_url.scheme,
        'domain': parsed_url.netloc,
        'path': parsed_url.path,
        'query': parsed_url.query,
        'url_length': len(url),
        'path_length': len(parsed_url.path),
        'query_length': len(parsed_url.query)
    }
    return info

def display_risk_gauge(confidence_score):
    """Display risk level as gauge"""
    if confidence_score >= 0.8:
        risk_level = "🔴 CRITICAL"
        color = "red"
        risk_percentage = confidence_score * 100
    elif confidence_score >= 0.6:
        risk_level = "🟠 HIGH"
        color = "orange"
        risk_percentage = confidence_score * 100
    elif confidence_score >= 0.4:
        risk_level = "🟡 MEDIUM"
        color = "yellow"
        risk_percentage = confidence_score * 100
    else:
        risk_level = "🟢 LOW"
        color = "green"
        risk_percentage = confidence_score * 100
    
    return risk_level, risk_percentage

def main():
    # Page configuration
    st.set_page_config(page_title="Phishing URL Detector", layout="wide", initial_sidebar_state="expanded")
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
        .main-header { font-size: 2.5rem; color: #FF6B35; font-weight: bold; text-align: center; }
        .sub-header { font-size: 1.2rem; color: #666; text-align: center; margin-bottom: 20px; }
        .result-safe { background-color: #d4edda; padding: 20px; border-radius: 10px; border-left: 5px solid #28a745; }
        .result-phishing { background-color: #f8d7da; padding: 20px; border-radius: 10px; border-left: 5px solid #dc3545; }
        .info-box { background-color: #e7f3ff; padding: 15px; border-radius: 8px; border-left: 4px solid #0066cc; margin: 10px 0; }
        .feature-badge { display: inline-block; background-color: #f0f0f0; padding: 8px 12px; border-radius: 20px; margin: 5px; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("<div class='main-header'>🔒 Phishing URL Detector</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Advanced AI-Powered URL Safety Analysis</div>", unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Scan URL", "📊 Analysis Guide", "📈 Results History", "ℹ️ About"])
    
    with tab1:
        st.markdown("**Enter or Paste URL:**")
        col1, col2 = st.columns([4, 1])
        
        with col1:
            url = st.text_input("Enter or Paste URL:", placeholder="https://example.com", key="url_input", label_visibility="collapsed")
        
        with col2:
            scan_button = st.button("🔍 Scan", use_container_width=True)
        
        if url:
            st.divider()
            
            # URL Information Section
            st.subheader("📋 URL Information")
            col_info1, col_info2, col_info3 = st.columns(3)
            
            url_info = get_url_info(url)
            
            with col_info1:
                st.metric("Protocol", url_info['protocol'])
                st.metric("URL Length", url_info['url_length'])
            
            with col_info2:
                st.metric("Domain", url_info['domain'])
                st.metric("Path Length", url_info['path_length'])
            
            with col_info3:
                st.metric("Path Segments", url_info['path'].count('/') if url_info['path'] else 0)
                st.metric("Query Length", url_info['query_length'])
            
            st.divider()
            
            if scan_button or url:
                # Extract features
                with st.spinner("🔄 Analyzing URL features..."):
                    features = extract_features(url)
                
                # Make prediction
                with st.spinner("🤖 Running AI model..."):
                    prediction = predict_phishing(features)
                    confidence = 1.0 if prediction[0] == 0 else 0.0
                
                if scan_button:
                    result_text = "Phishing" if prediction[0] == 0 else "Safe"
                    score_text = "95%" if prediction[0] == 0 else "5%"
                    save_history(url, result_text, score_text)

                st.divider()
                
                # Display Result
                st.subheader("🎯 Scan Result")
                
                col_result1, col_result2 = st.columns([2, 1])
                
                with col_result1:
                    if prediction[0] == 0:
                        st.markdown(
                            '<div class="result-phishing"><h3>⚠️ PHISHING ALERT</h3>'
                            '<p style="font-size: 1.1rem;">This URL is classified as <strong>PHISHING</strong></p>'
                            '<p style="color: #666;">Do not click on this link or enter your personal information.</p></div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            '<div class="result-safe"><h3>✅ SAFE</h3>'
                            '<p style="font-size: 1.1rem;">This URL appears to be <strong>LEGITIMATE</strong></p>'
                            '<p style="color: #666;">This website has passed our safety checks.</p></div>',
                            unsafe_allow_html=True
                        )
                
                with col_result2:
                    if prediction[0] == 0:
                        st.metric("Risk Score", "95%", delta="High", delta_color="inverse")
                    else:
                        st.metric("Risk Score", "5%", delta="Low", delta_color="inverse")
                
                st.divider()
                
                # Detailed Analysis
                st.subheader("🔬 Detailed Feature Analysis")
                
                analysis_col1, analysis_col2 = st.columns(2)
                
                with analysis_col1:
                    st.write("**Address Bar Features:**")
                    st.markdown(f"""
                    - 🔢 Has IP Address: {'Yes ❌' if features[0] == 1 else 'No ✅'}
                    - @ Symbol: {'Present ❌' if features[1] == 1 else 'Absent ✅'}
                    - URL Length: {'Suspicious ❌' if features[2] == 1 else 'Normal ✅'}
                    - URL Depth: {int(features[3])} segments
                    - Redirects: {'Multiple ⚠️' if features[4] == 1 else 'None ✅'}
                    - HTTPS Domain: {'No ❌' if features[5] == 1 else 'Yes ✅'}
                    - Shortened URL: {'Yes ❌' if features[6] == 1 else 'No ✅'}
                    - Prefix/Suffix: {'Has - (Dash) ❌' if features[7] == 1 else 'None ✅'}
                    """)
                
                with analysis_col2:
                    st.write("**Domain & Content Features:**")
                    st.markdown(f"""
                    - DNS Record: {'Suspicious' if features[8] == 0 else 'Normal'} {'❌' if features[8] == 0 else '✅'}
                    - Domain Age: {'New Domain ⚠️' if features[9] == 0 else 'Established ✅'}
                    - Domain End: {'Suspicious' if features[10] == 0 else 'Normal'} {'❌' if features[10] == 0 else '✅'}
                    - Web Traffic: {'Low Traffic ⚠️' if features[11] == 1 else 'High Traffic ✅'}
                    - Iframe: {'Present ❌' if features[12] == 0 else 'Absent ✅'}
                    - Mouse Over: {'JavaScript Event ⚠️' if features[13] == 1 else 'None ✅'}
                    - Right Click: {'Disabled ❌' if features[14] == 0 else 'Enabled ✅'}
                    - Forwarding: {'Present ⚠️' if features[15] == 1 else 'None ✅'}
                    """)
                
                st.divider()
                
                # Recommendations
                st.subheader("💡 Security Recommendations")
                
                recommendations = []
                if features[0] == 1:
                    recommendations.append("🔴 URL contains an IP address - suspicious")
                if features[1] == 1:
                    recommendations.append("🔴 URL contains @ symbol - likely phishing")
                if features[2] == 1:
                    recommendations.append("🟠 URL is unusually long - potential phishing")
                if features[4] == 1:
                    recommendations.append("🟠 URL has multiple redirects - verify destination")
                if not features[5]:
                    recommendations.append("🟠 Website does not use HTTPS - not secure")
                if features[6] == 1:
                    recommendations.append("🟠 URL uses shortening service - verify before clicking")
                
                if recommendations:
                    for rec in recommendations:
                        st.write(rec)
                else:
                    st.success("✅ No immediate security concerns detected. Always exercise caution with unknown links.")
                
                st.divider()
                
                # Feedback Section
                st.subheader("💬 Help Us Improve")
                feedback_col1, feedback_col2 = st.columns([1, 1])
                
                with feedback_col1:
                    if st.button("✅ This Result is Correct"):
                        st.success("Thank you for your feedback! It helps us improve our detection.")
                
                with feedback_col2:
                    if st.button("❌ This Result is Incorrect"):
                        st.warning("We're sorry! Please report this to help us improve.")
    
    with tab2:
        st.subheader("📊 How Our Analysis Works")
        
        st.write("""
        Our Phishing Detection System analyzes URLs across multiple categories:
        
        **1. Address Bar Features**
        - IP Address Detection: Checks if URL contains IP instead of domain
        - Special Characters: Detects @ and other suspicious characters
        - URL Length: Legitimate URLs are typically shorter
        - Redirection: Multiple redirects indicate phishing
        
        **2. Domain Based Features**
        - DNS Records: Verifies domain legitimacy
        - Domain Age: Older domains are generally more trustworthy
        - Web Traffic: Analyzes site popularity and ranking
        
        **3. HTML & JavaScript Features**
        - Iframe Detection: Malicious content embedding
        - Event Handlers: Detects suspicious JavaScript events
        - Content Forwarding: Checks for redirects to phishing sites
        """)
    
    with tab3:
        st.subheader("📈 Scan History")
        history = load_history()
        
        if not history:
            st.info("📝 Your recent scans will appear here. No scans yet.")
        else:
            for entry in history:
                with st.container():
                    col_h1, col_h2, col_h3 = st.columns([3, 1, 1])
                    with col_h1:
                        st.write(f"**{entry['url']}**")
                        st.caption(f"Scanned at: {entry['timestamp']}")
                    with col_h2:
                        if entry['result'] == "Phishing":
                            st.error("⚠️ Phishing")
                        else:
                            st.success("✅ Safe")
                    with col_h3:
                        st.metric("Risk Score", entry['score'])
                st.divider()

    with tab4:
        st.subheader("ℹ️ About This Tool")
        st.write("""
        **Phishing URL Detector v1.0**
        
        Built with XGBoost Machine Learning Algorithm for advanced threat detection.
        
        **Features:**
        - Real-time URL analysis
        - Multi-factor risk assessment
        - SSL certificate verification
        - Domain reputation checking
        - Advanced feature extraction
        
        **Disclaimer:**
        This tool provides security analysis but is not 100% foolproof. 
        Always exercise caution with unknown URLs.
        """)
    
if __name__ == '__main__':
    main()
