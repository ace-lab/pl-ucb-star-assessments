# Testing Legacy Code - S15 quiz 2 & open-response-exam-questions repo

Lucky you, you've been assigned to take over Barbara Bitdiddle's old app for managing customers of an online business!  She hasn't touched the code in months and you've never seen it before, so, hello legacy code.

The basic model is a Customer, and your job is to create some tests for the code that lets a customer update their email address in the app.  Apparently the happy path has tests, but the sad path (when the customer tries to provide an invalid email address) doesn't.

You find the following routes in config/routes.rb:

get '/customers/:id/edit_email', :controller => 'customers', :action => 'edit_email'
post '/customers/:id/update_email',:controller => 'customers',:action => 'update_email'

And here is the controller action called to actually process the update, which you will write a couple of RSpec specs for:

class CustomersController
  def update_email
    customer = Customer.find(params[:id])
    new_email = params[:email]
    begin 
      Emailer.send_confirmation(new_email)
      customer.update_attributes(:email => new_email)
    rescue Emailer::UndeliverableError
      flash[:notice] = "That email address cannot be delivered to."
    end
  end 
end
Question 11 [1 point] Warmup
Choose ONE. The params[] hash in this example will be populated from which sources? (Assume there is no AJAX code in the app.)
The route URL only
An HTML form only
The route URL and an HTML form
Cannot tell from the information given

Question 12 [9 points] Write the RSpec controller spec
Happily, Barbara's code includes a FactoryGirl factory to create instances of Customer for use in tests:

FactoryGirl.create(:customer, attributes)

where attributes is a hash of the desired attributes, or if omitted, default attributes are used.

Fill in the RSpec controller test that checks the sad path when a network error happens. On the last page of the quiz is an RSpec cheat sheet you may find helpful.

Skeleton code is provided on the answer sheet.

describe "when undeliverable address provided" do
  before :each do
   @customer = FactoryGirl.create(:customer, :email => 'old_email@aol.com')
   @params = {:id => @customer.id, :email => 'new_email@aol.com'}
   Emailer.stub(:send_confirmation).and_raise(Emailer::UndeliverableError)
  end
  it "should not change customer's original email" do
    post :update_email, @params
    # check that customer's email did not get changed:
    @customer.email.should == 'old_email@aol.com'
  end
  it "should display error message" do
    post :update_email,  @params
    flash[:notice].should == "That email address cannot be delivered to."
  end
end

It is fine if you manually built a params hash rather than passing the provided @params, but your hash MUST include both the :id and :email attributes to be correct.

Question 13 [5 points] Write part of the Cuke scenario

Now it's time to create some Cucumber scenarios to test the above flow. 
Here are the first two steps of a scenario for testing this interaction:

Given a customer named "John Doe" with email "jd@gmail.com" exists
When I visit the email update page for that customer

Fill in the step definitions for just the two above steps.   (You don’t need to add additional steps in the scenario.)  You should assume the app does not have access to the web_steps.rb prepackaged steps file. On the last page of the quiz is a Capybara cheat sheet you may find helpful. Also as a reminder, here are those two lines from config/routes.rb so you don't have to flip back to the previous page:

Skeleton code is provided on the answer sheet.

get '/customers/:id/edit_email', :controller => 'customers', :action => 'edit_email'
post '/customers/:id/update_email',:controller => 'customers',:action => 'update_email'

Given /^a customer named "(.*)" with email "(.*)" exists$/ do |name, email|
  @customer = FactoryGirl.create(:customer, :name => name, :email => email)
end

When /^I visit the email update page for that customer$/ do
  visit "/customers/#{@customer.id}/edit_email"
end

You're not required to use Factory Girl to create the customer for the test, but if you create it manually, you must provide legal attribute values and you must check if creation fails, either by using #create! or by checking return value of #create.  (FactoryGirl always raises an exception if creation fails.)
