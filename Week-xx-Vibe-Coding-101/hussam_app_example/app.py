import streamlit as st
from PIL import Image
import io

# Page configuration
st.set_page_config(
    page_title="AI Image Generator",
    page_icon="🎨",
    layout="wide"
)

# Title and description
st.title("🎨 AI Image Generator")
st.markdown("Generate amazing images from text descriptions using AI!")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Model selection
    model_choice = st.selectbox(
        "Select Model",
        [
            "Stable Diffusion Turbo (Fast, Low Memory)",
            "Stable Diffusion 1.5 (Good Quality)"
        ],
        index=0,
        help="SD Turbo is 4x faster and uses less memory - perfect for demos!"
    )
    
    # Image settings
    st.subheader("Image Settings")
    width = st.slider("Width", 256, 1024, 512, step=64)
    height = st.slider("Height", 256, 1024, 512, step=64)
    num_inference_steps = st.slider("Quality Steps", 10, 100, 50)
    guidance_scale = st.slider("Guidance Scale", 1.0, 20.0, 7.5, step=0.5)

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Enter your prompt")
    
    # Text input for user prompt
    user_prompt = st.text_area(
        "Describe the image you want to generate:",
        placeholder="A beautiful sunset over mountains with a lake in the foreground...",
        height=100,
        help="Be descriptive! The more details you provide, the better the result."
    )
    
    # Generate button
    generate_button = st.button(
        "🚀 Generate Image",
        type="primary",
        use_container_width=True
    )

with col2:
    st.subheader("🖼️ Generated Image")
    
    # Placeholder for generated image
    if generate_button:
        if user_prompt.strip():
            with st.spinner("Generating your image... This may take a few minutes."):
                try:
                    # Try to import diffusers dynamically
                    try:
                        import torch
                        from diffusers import StableDiffusionPipeline
                        
                        # Check if model is already loaded in session state
                        if 'model' not in st.session_state or st.session_state.get('current_model') != model_choice:
                            with st.spinner("Loading AI model... This may take a few minutes on first run."):
                                # Simple model selection - only 2 reliable options
                                if "Turbo" in model_choice:
                                    model_id = "stabilityai/sd-turbo"
                                    optimal_steps = 4
                                else:
                                    model_id = "runwayml/stable-diffusion-v1-5"
                                    optimal_steps = 20  # Reduced for faster generation
                                
                                # Load the model with minimal memory usage
                                st.session_state.model = StableDiffusionPipeline.from_pretrained(
                                    model_id, 
                                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                                    safety_checker=None,
                                    requires_safety_checker=False,
                                    use_safetensors=True  # More memory efficient
                                )
                                
                                # Move to GPU if available
                                if torch.cuda.is_available():
                                    st.session_state.model = st.session_state.model.to("cuda")
                                
                                # Store current model choice
                                st.session_state.current_model = model_choice
                                st.session_state.model_steps = optimal_steps
                        
                        # Generate image
                        with torch.no_grad():
                            # Use model-specific optimal steps
                            optimal_steps = st.session_state.get('model_steps', 50)
                            actual_steps = min(num_inference_steps, optimal_steps)
                            
                            # For Turbo models, use fewer steps and lower guidance
                            if "Turbo" in model_choice:
                                actual_steps = min(actual_steps, 4)
                                actual_guidance = min(guidance_scale, 1.0)
                            else:
                                actual_guidance = guidance_scale
                            
                            image = st.session_state.model(
                                user_prompt,
                                width=width,
                                height=height,
                                num_inference_steps=actual_steps,
                                guidance_scale=actual_guidance
                            ).images[0]
                        
                        st.image(image, caption=f"Generated: '{user_prompt}'", use_container_width=True)
                        st.success(f"✅ Generated image for: '{user_prompt}'")
                        
                    except ImportError as e:
                        st.error(f"❌ Missing dependencies: {str(e)}")
                        st.info("🔧 Please install the required packages: pip install -r requirements.txt")
                        
                        # Show placeholder image
                        placeholder_image = Image.new('RGB', (width, height), color='lightblue')
                        st.image(placeholder_image, caption="Placeholder - Install dependencies to generate real images", use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"❌ Error generating image: {str(e)}")
                        st.info("💡 This might be due to missing CUDA drivers or insufficient memory.")
                        
                        # Show placeholder image
                        placeholder_image = Image.new('RGB', (width, height), color='lightblue')
                        st.image(placeholder_image, caption="Error occurred - showing placeholder", use_container_width=True)
                    
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")
        else:
            st.warning("⚠️ Please enter a prompt to generate an image.")
