# Whiskr user stories

You are working on Whiskr, which is Tinder for whiskey lovers with cats. One feature of the application is that users can sign up with their name and email. Let’s write some Cucumber steps to test out this feature:

```
Feature: signup for an account
  As a whiskey-drinking cat lover
  So that I can socialize with other similar people
  I want to signup for an account on Whiskr.com

Given I am on the signup page
When I fill in the signup form with name: "Ernest Hemingway" and email: "catlover99@gmail.com"
And I press "Sign Up"
Then a user with email "catlover99@gmail.com" should exist
```

The routes file contains these routes, among others:

```
resources :users
get '/signup', :controller => 'users', :action => 'signup'
post '/signup', :controller => 'users', :action => 'create_signup'
```

The ActiveRecord model for User has the following attributes:  `name (string), email (string)`

Fill in the step definitions for the above steps, and the body of the create_signup controller method, in the provided code skeleton.   (You don’t need to add additional steps in the scenario.)  You should assume the app does not have access to the web_steps.rb prepackaged steps file. On the last page of the quiz is a Capybara cheat sheet you may find helpful. Assume for the user form that only the name and email are required to register, without a password. 

File `user_steps.rb:`

```
Given /^I am on the signup page$/ do
  visit "/signup"
end

When /^I fill in the signup form 
with name: “([^”]*)” and email: “([^”]*)”$/ do |name,email| # Q3.1[2]
	# Q3.2 [2] your code here #
	fill_in(“name”, name)
	fill_in(“email”, email)
end

When /^I press "Sign Up"$/ do
	# Q3.3 [2] your code here 
	click_button(“Sign Up”)

end

Then /^A user with email: “([^”]*)” should exist$/ do |email|  # Q3.4[2]
     # Q3.5 [4] your code here
	expect(User.where(email: email)).not_to be_nil
end
```

File `users_controller.rb`: 

```
class UsersController < ApplicationController

  def create_signup					# Q3.5 [2]

    params.require( :name, :email )	      	# Q3.6 [2]
    @user = User.create(params) 			# Q3.7 [4]

    redirect_to user_path(@user)
  end
end
```

# Capybara Cheat sheet

Transcribe [this cheat
sheet](https://drive.google.com/drive/u/0/folders/0BxKnkWLvWBrTV2NsVjdmMXdYNnc?resourcekey=0-ivAvycZRI_S1uSx1UNZiFw)


