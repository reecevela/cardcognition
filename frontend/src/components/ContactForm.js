import React from 'react';
import { useForm, ValidationError } from '@formspree/react';
import './ContactForm.css'

function ContactForm() {
  const [state, handleSubmit] = useForm("xjvddevj");
  if (state.succeeded) {
      return <p>Thanks you!</p>;
  }
  return (
    <div className='contact-form-wrapper'>
      <h1>Contact Us</h1>
      <p>Have a question or comment? Feature suggestion? Issue? Send it my way!</p>
      <div className='contact-form'>
        <form onSubmit={handleSubmit}>
          <label htmlFor="email">
            Email Address
          </label>
          <input
            id="email"
            type="email" 
            name="email"
          />
          <ValidationError 
            prefix="Email" 
            field="email"
            errors={state.errors}
          />
          <label htmlFor="message">
            Message
          </label>
          <textarea
            id="message"
            name="message"
          />
          <ValidationError 
            prefix="Message" 
            field="message"
            errors={state.errors}
          />
          <button type="submit" disabled={state.submitting}>
            Submit
          </button>
        </form>
      </div>
    </div>
  );
}

export default ContactForm;
